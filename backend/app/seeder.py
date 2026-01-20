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

ENGINE_REGISTRY = [
    {"key": "social", "name": "Social Feed", "icon": "💬", "description": "Reddit-style posts."},
    {"key": "senate", "name": "The Senate", "icon": "⚖️", "description": "Governance."},
    {"key": "arena", "name": "Arena", "icon": "🏆", "description": "Match schedules."},
    {"key": "bazaar", "name": "Bazaar", "icon": "🛍️", "description": "Marketplace."},
    {"key": "academy", "name": "Academy", "icon": "🎓", "description": "LMS courses."},
    {"key": "club", "name": "Club Events", "icon": "🎉", "description": "RSVPs."},
    {"key": "library", "name": "Library", "icon": "📚", "description": "Wiki pages."},
    {"key": "stage", "name": "The Stage", "icon": "🎥", "description": "Video feed."},
    {"key": "bunker", "name": "The Bunker", "icon": "☢️", "description": "Encrypted chat."},
    {"key": "guild", "name": "Guild", "icon": "💰", "description": "Bounties."},
    {"key": "garden", "name": "Garden", "icon": "🌻", "description": "Habit tracking."},
]

async def seed_db():
    print("🚀 INITIALIZING THE NEXUS: TOTAL SYSTEM SEED...")
    
    async with engine.begin() as conn:
        print("🔥 Forced Wipe in Progress...")
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        for table in result.scalars().all():
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
        print("🏗️  Rebuilding Tables...")
        await conn.run_sync(SQLModel.metadata.create_all)
        
    async with async_session_factory() as db:
        # 1. ENGINES
        engine_map = {}
        for e in ENGINE_REGISTRY:
            eng = Engine(**e)
            db.add(eng); await db.commit(); await db.refresh(eng)
            engine_map[e["key"]] = eng.id

        # 2. USERS
        admin = User(email=ADMIN_EMAIL, full_name="Resinen Architect", hashed_password=get_password_hash(ADMIN_PASS), is_superuser=True)
        db.add(admin)
        users = []
        for u in TEST_USERS:
            new_user = User(email=u["email"], full_name=u["name"], hashed_password=get_password_hash(u["pass"]))
            db.add(new_user); users.append(new_user)
        await db.commit()
        for u in users: await db.refresh(u)
        alice, bob = users[0], users[1]

        # 3. THE WORLD (THE NEXUS)
        nexus = Community(
            name="The Nexus", slug="nexus", description="The world where every engine is installed.",
            archetypes=[a for a in Archetype], creator_id=admin.id
        )
        db.add(nexus); await db.commit(); await db.refresh(nexus)
        cid = nexus.id

        # 4. INSTALL EVERYTHING
        for eid in engine_map.values():
            db.add(CommunityEngine(community_id=cid, engine_id=eid, is_active=True))
        
        db.add(Membership(user_id=alice.id, community_id=cid, role="member"))
        db.add(Membership(user_id=bob.id, community_id=cid, role="moderator"))
        
        gen_chap = Chapter(community_id=cid, title="General", description="Main Hub")
        db.add(gen_chap); await db.commit(); await db.refresh(gen_chap)

        # 5. ENGINE CONTENT (THE GAUNTLET)
        print("⚡ Populating Engines...")

        # Social
        p1 = Post(community_id=cid, chapter_id=gen_chap.id, author_id=admin.id, title="System Online", content="The Nexus is live.")
        db.add(p1); await db.commit(); await db.refresh(p1)
        db.add(PostLike(user_id=alice.id, post_id=p1.id))
        db.add(Comment(post_id=p1.id, user_id=bob.id, content="Ready for testing."))

        # Arena
        t1 = ArenaTeam(community_id=cid, name="Titans", color="#FF4444")
        t2 = ArenaTeam(community_id=cid, name="Phantoms", color="#4444FF")
        db.add(t1); db.add(t2); await db.commit(); await db.refresh(t1); await db.refresh(t2)
        match = ArenaMatch(community_id=cid, team_a_id=t1.id, team_b_id=t2.id, status=MatchStatus.LIVE, score_a=1, score_b=0)
        db.add(match)

        print("💰 Seeding Guild Bounties...")
        db.add(GuildBounty(
            community_id=cid, 
            author_id=admin.id, 
            title="Bug Hunt", 
            description="Find and document memory leaks in the Nexus core logic.", # 🚨 ADD THIS LINE
            reward_text="1000 CR"
        ))
        # Senate
        db.add(Proposal(community_id=cid, author_id=admin.id, title="Nexus Expansion", ends_at=datetime.utcnow() + timedelta(days=7)))

        # Club & Stage
        db.add(ClubEvent(community_id=cid, creator_id=bob.id, title="Nexus Rave", start_time=datetime.utcnow() + timedelta(days=1)))
        db.add(StageVideo(community_id=cid, author_id=alice.id, title="Nexus Cinematic", video_url="https://www.youtube.com/embed/dQw4w9WgXcQ"))

        # Library & Bunker & Bazaar
        db.add(LibraryPage(community_id=cid, author_id=admin.id, slug="rules", title="Nexus Rules", content="1. No Spam."))
        db.add(BunkerMessage(community_id=cid, author_id=alice.id, content="Secret Nexus Key: 7712"))
        db.add(Listing(community_id=cid, curator_id=bob.id, title="Nexus Blade", price_display="50 Gold"))

        # Garden
        habit = GardenHabit(community_id=cid, user_id=alice.id, title="Core Logic Review", icon="🧠")
        db.add(habit)

        await db.commit()
        print("✅ THE NEXUS IS FULLY OPERATIONAL.")

if __name__ == "__main__":
    asyncio.run(seed_db())