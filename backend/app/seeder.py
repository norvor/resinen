import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlmodel import SQLModel, select
from app.core.database import async_session_factory, engine 
from app.core.security import get_password_hash

# --- CORE MODELS ---
from app.models.user import User
from app.models.community import Community, Membership, Chapter, Archetype
from app.models.engine import Engine, CommunityEngine

# --- ENGINE MODELS ---
from app.models.social import Post, Comment, PostLike
from app.models.listing import Listing, ListingVouch
from app.models.governance import Proposal, ProposalStatus, ProposalVote, VoteType
from app.models.academy import Module, Lesson, LessonCompletion
from app.models.arena import ArenaTeam, ArenaMatch, MatchStatus, ArenaPrediction
from app.models.club import ClubEvent, ClubRSVP, RSVPStatus
from app.models.library import LibraryPage
from app.models.stage import StageVideo
from app.models.bunker import BunkerMessage
from app.models.guild import GuildProject, GuildBounty, BountyStatus
from app.models.garden import GardenHabit, GardenLog

# --- CONSTANTS ---
ADMIN_EMAIL = "admin@resinen.com"
ADMIN_PASS = "admin123"

TEST_USERS = [
    {"email": "alice@resinen.com", "name": "Alice Builder", "pass": "alice123", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice"},
    {"email": "bob@resinen.com", "name": "Bob Gamer", "pass": "bob123", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob"},
]

# The "App Store" Registry
ENGINE_REGISTRY = [
    {"key": "social", "name": "Social Feed", "icon": "message-circle", "description": "Reddit-style posts and comments."},
    {"key": "senate", "name": "The Senate", "icon": "scale", "description": "Governance and proposals."},
    {"key": "arena", "name": "Arena", "icon": "trophy", "description": "Match schedules and scorekeeping."},
    {"key": "bazaar", "name": "Bazaar", "icon": "shopping-bag", "description": "P2P Marketplace."},
    {"key": "academy", "name": "Academy", "icon": "book-open", "description": "LMS for courses and lessons."},
    {"key": "club", "name": "Club Events", "icon": "calendar", "description": "RSVP and event management."},
    {"key": "library", "name": "Library", "icon": "archive", "description": "Wiki and documentation."},
    {"key": "stage", "name": "The Stage", "icon": "film", "description": "Video feed and broadcasting."},
    {"key": "bunker", "name": "The Bunker", "icon": "shield", "description": "Ephemeral encrypted chat."},
    {"key": "guild", "name": "Guild", "icon": "briefcase", "description": "Bounties and projects."},
    {"key": "garden", "name": "Garden", "icon": "sprout", "description": "Habit tracking and resources."},
]

WORLDS = [
    {
        "name": "The Colosseum", "slug": "colosseum", "archetypes": [Archetype.ARENA, Archetype.LOUNGE],
        "description": "Where champions are forged.",
        "engines": ["arena", "social", "bunker"]
    },
    {
        "name": "Builders Guild", "slug": "builders", "archetypes": [Archetype.GUILD, Archetype.ACADEMY],
        "description": "Ship code, get paid.",
        "engines": ["guild", "academy", "social", "library"]
    },
    {
        "name": "The Capitol", "slug": "capitol", "archetypes": [Archetype.SENATE],
        "description": "Governance and debate.",
        "engines": ["senate", "library"]
    },
    {
        "name": "Grand Bazaar", "slug": "bazaar", "archetypes": [Archetype.BAZAAR],
        "description": "The finest goods.",
        "engines": ["bazaar", "social"]
    },
    {
        "name": "Neon Nights", "slug": "neon", "archetypes": [Archetype.CLUB, Archetype.STAGE],
        "description": "Music, events, and vibes.",
        "engines": ["club", "stage", "social"]
    },
    {
        "name": "Zen Garden", "slug": "zen", "archetypes": [Archetype.GARDEN],
        "description": "Daily habits and peace.",
        "engines": ["garden", "library"]
    }
]

async def seed_db():
    print("🌱 STARTING COMPREHENSIVE SEEDER...")
    
    # 1. WIPE DB
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✨ Database Wiped & Rebuilt.")

    async with async_session_factory() as db:
        
        # 2. SEED ENGINE REGISTRY (App Store)
        print("🔧 Seeding Engine Registry...")
        engine_map = {} # key -> uuid
        for e_data in ENGINE_REGISTRY:
            eng = Engine(key=e_data["key"], name=e_data["name"], description=e_data["description"], icon=e_data["icon"])
            db.add(eng)
            await db.commit()
            await db.refresh(eng)
            engine_map[e_data["key"]] = eng.id

        # 3. SEED USERS
        print("👤 Seeding Users...")
        # Admin
        admin = User(
            email=ADMIN_EMAIL, full_name="Resinen Architect", hashed_password=get_password_hash(ADMIN_PASS),
            is_active=True, is_superuser=True, level=99, reputation_score=9000,
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=admin"
        )
        db.add(admin)
        
        # Alice & Bob
        users = []
        for u in TEST_USERS:
            new_user = User(
                email=u["email"], full_name=u["name"], hashed_password=get_password_hash(u["pass"]),
                is_active=True, level=5, reputation_score=100, avatar_url=u["avatar"]
            )
            db.add(new_user)
            users.append(new_user)
        
        await db.commit()
        await db.refresh(admin)
        for u in users: await db.refresh(u)
        
        alice, bob = users[0], users[1]

        # 4. SEED WORLDS
        print("🌍 Seeding Worlds & Content...")
        
        for w_data in WORLDS:
            # Create Community
            comm = Community(
                name=w_data["name"], slug=w_data["slug"], description=w_data["description"],
                archetypes=w_data["archetypes"], creator_id=admin.id,
                banner_url=f"https://source.unsplash.com/random/1200x400/?{w_data['slug']}"
            )
            db.add(comm)
            await db.commit()
            await db.refresh(comm)
            cid = comm.id
            
            # Create Memberships
            db.add(Membership(user_id=alice.id, community_id=cid, role="member"))
            db.add(Membership(user_id=bob.id, community_id=cid, role="moderator"))
            
            # Install Engines
            for eng_key in w_data["engines"]:
                if eng_key in engine_map:
                    db.add(CommunityEngine(community_id=cid, engine_id=engine_map[eng_key], is_active=True))

            # Create Chapters (Channels)
            general_chap = Chapter(community_id=cid, title="General", description="Chat about anything")
            ann_chap = Chapter(community_id=cid, title="Announcements", description="Read only")
            db.add(general_chap); db.add(ann_chap)
            await db.commit()
            await db.refresh(general_chap)

            # --- ENGINE SPECIFIC DATA ---

            # A. SOCIAL (The Feed)
            if "social" in w_data["engines"]:
                # Post by Admin
                p1 = Post(
                    community_id=cid, chapter_id=general_chap.id, author_id=admin.id,
                    title="Welcome to " + w_data["name"], content="Let's build something great together.",
                    is_pinned=True, like_count=2
                )
                db.add(p1)
                await db.commit()
                await db.refresh(p1)
                
                # Interactions
                db.add(PostLike(user_id=alice.id, post_id=p1.id))
                db.add(PostLike(user_id=bob.id, post_id=p1.id))
                db.add(Comment(post_id=p1.id, author_id=alice.id, content="Glad to be here!"))

            # B. ARENA (Sports)
            if "arena" in w_data["engines"]:
                t1 = ArenaTeam(community_id=cid, name="Red Dragons", short_code="RED")
                t2 = ArenaTeam(community_id=cid, name="Blue Knights", short_code="BLU")
                db.add(t1); db.add(t2)
                await db.commit()
                await db.refresh(t1); await db.refresh(t2)
                
                match = ArenaMatch(
                    community_id=cid, team_a_id=t1.id, team_b_id=t2.id, 
                    status=MatchStatus.LIVE, start_time=datetime.utcnow(), 
                    score_a=2, score_b=1, time_display="75'"
                )
                db.add(match)
                await db.commit()
                await db.refresh(match)
                
                # Alice predicts Red
                db.add(ArenaPrediction(user_id=alice.id, match_id=match.id, picked_team_id=t1.id))

            # C. GUILD (Projects)
            if "guild" in w_data["engines"]:
                proj = GuildProject(
                    community_id=cid, author_id=bob.id, title="Resinen API", 
                    description="The backend powering this city.", tech_stack="Python, FastAPI", likes=1
                )
                db.add(proj)
                db.add(GuildBounty(
                    community_id=cid, author_id=admin.id, title="Fix Login Bug", 
                    description="Token expires too fast.", reward_text="$500 Bounty", status=BountyStatus.OPEN
                ))

            # D. BAZAAR (Listings)
            if "bazaar" in w_data["engines"]:
                lst = Listing(
                    community_id=cid, curator_id=alice.id, title="Mechanical Keyboard", 
                    description="Keychron Q1, barely used.", price_display="$150", 
                    link_url="https://ebay.com/item/123", vouch_count=1
                )
                db.add(lst)
                await db.commit()
                await db.refresh(lst)
                db.add(ListingVouch(user_id=bob.id, listing_id=lst.id))

            # E. ACADEMY (Courses)
            if "academy" in w_data["engines"]:
                mod = Module(community_id=cid, title="101: Fundamentals", order_index=0)
                db.add(mod)
                await db.commit()
                await db.refresh(mod)
                les = Lesson(module_id=mod.id, title="Setup", content_body="Install Python...", duration_min=10)
                db.add(les)
                await db.commit()
                await db.refresh(les)
                # Alice finished the lesson
                db.add(LessonCompletion(user_id=alice.id, lesson_id=les.id))

            # F. SENATE (Governance)
            if "senate" in w_data["engines"]:
                prop = Proposal(
                    community_id=cid, author_id=admin.id, title="CIP-1: Upgrade Server", 
                    description="We need more RAM.", status=ProposalStatus.ACTIVE,
                    votes_yes=1, ends_at=datetime.utcnow() + timedelta(days=2)
                )
                db.add(prop)
                await db.commit()
                await db.refresh(prop)
                db.add(ProposalVote(user_id=bob.id, proposal_id=prop.id, choice=VoteType.YES))

            # G. CLUB (Events)
            if "club" in w_data["engines"]:
                evt = ClubEvent(
                    community_id=cid, creator_id=bob.id, title="Friday Night Mixer", 
                    description="Drinks and code.", location_name="Lounge", 
                    start_time=datetime.utcnow() + timedelta(days=2), count_going=1
                )
                db.add(evt)
                await db.commit()
                await db.refresh(evt)
                db.add(ClubRSVP(user_id=alice.id, event_id=evt.id, status=RSVPStatus.GOING))

            # H. LIBRARY (Wiki)
            if "library" in w_data["engines"]:
                root_page = LibraryPage(community_id=cid, author_id=admin.id, slug="home", title="Wiki Home", content="# Welcome")
                db.add(root_page)
                await db.commit()
                await db.refresh(root_page)
                db.add(LibraryPage(community_id=cid, author_id=bob.id, slug="rules", title="Rules", content="No spam.", parent_id=root_page.id))

            # I. STAGE (Videos)
            if "stage" in w_data["engines"]:
                db.add(StageVideo(
                    community_id=cid, author_id=alice.id, title="My Setup Tour", 
                    video_url="https://www.youtube.com/embed/dQw4w9WgXcQ", thumbnail_url="https://source.unsplash.com/random/300x500", 
                    view_count=102, like_count=5
                ))

            # J. BUNKER (Chat)
            if "bunker" in w_data["engines"]:
                db.add(BunkerMessage(
                    community_id=cid, author_id=bob.id, content="Code is 4421. Delete this.", 
                    is_anonymous=True, expires_at=datetime.utcnow() + timedelta(minutes=30)
                ))

            # K. GARDEN (Habits)
            if "garden" in w_data["engines"]:
                habit = GardenHabit(community_id=cid, user_id=alice.id, title="Drink Water", icon="💧", streak_current=5)
                db.add(habit)
                await db.commit()
                await db.refresh(habit)
                db.add(GardenLog(habit_id=habit.id, log_date=datetime.utcnow().date()))

        await db.commit()
        print("✅ GENESIS COMPLETE. SYSTEM READY.")

if __name__ == "__main__":
    asyncio.run(seed_db())