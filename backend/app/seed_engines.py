import asyncio
from sqlmodel import select
from app.core.database import async_session_factory
from app.models.engine import Engine

# Matches your Backend Routers and Svelte Component Map
SYSTEM_ENGINES = [
    {"key": "social", "name": "The Lounge", "icon": "🛋️", "description": "Social Feed & Threads"},
    {"key": "arena", "name": "The Arena", "icon": "🏆", "description": "Sports & Betting"},
    {"key": "stage", "name": "The Stage", "icon": "🎤", "description": "Live Events"},
    {"key": "library", "name": "The Library", "icon": "📚", "description": "Wiki & Docs"},
    {"key": "guild", "name": "The Guild", "icon": "⚒️", "description": "Bounties & Projects"},
    {"key": "listings", "name": "The Bazaar", "icon": "🏷️", "description": "Marketplace"},
    {"key": "governance", "name": "The Senate", "icon": "⚖️", "description": "Proposals & Voting"},
    {"key": "academy", "name": "The Academy", "icon": "🎓", "description": "Education"},
    {"key": "club", "name": "The Club", "icon": "🥂", "description": "Events & RSVPs"},
    {"key": "bunker", "name": "The Bunker", "icon": "🕵️", "description": "Encrypted Comms"},
    {"key": "garden", "name": "The Sanctuary", "icon": "🙏", "description": "Habits & Growth"},
    {"key": "referral", "name": "Referral", "icon": "🔗", "description": "Invites"}
]

async def seed_engines():
    print("⚙️ Seeding System Engines...")
    async with async_session_factory() as session:
        for eng in SYSTEM_ENGINES:
            # Check if exists to avoid duplicates
            existing = await session.execute(select(Engine).where(Engine.key == eng["key"]))
            if not existing.scalars().first():
                print(f"   -> Creating {eng['name']} ({eng['key']})")
                session.add(Engine(**eng))
            else:
                print(f"   -> Skipped {eng['key']} (Exists)")
        await session.commit()
    print("✅ Engines Online.")

if __name__ == "__main__":
    asyncio.run(seed_engines())