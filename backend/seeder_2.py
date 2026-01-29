import asyncio
from sqlmodel import select
from app.database import async_session_factory
from app.models import (
    User, BudgetWidget, HabitWidget, ScribbleWidget, TravelWidget, 
    TaskWidget, NoteWidget, LoveWidget, Mission
)
from passlib.context import CryptContext

# Setup Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 📝 EDIT THIS LIST TO ADD NEW USERS ---
NEW_USERS = [
    "guestone@resinen.com",
    "guesttwo@resinen.com",
]

async def seed_additional():
    print("🌱 Starting Additional Seeding (Safe Mode)...")
    
    async with async_session_factory() as session:
        for email in NEW_USERS:
            # 1. CHECK IF USER EXISTS
            statement = select(User).where(User.email == email)
            result = await session.execute(statement)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"   ⚠️  Skipping {email} (Already exists)")
                continue

            print(f"   -> Creating user: {email}...")
            
            # 2. CREATE USER
            user = User(
                email=email,
                hashed_password=pwd_context.hash("password123"),
                is_premium=True,
                country_code="IN"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            # 3. ADD WIDGETS & DATA
            # --- Mission Control ---
            m1 = Mission(
                user_id=user.id,
                codename="OPERATION: EXPANSION",
                rune="🚀",
                color="#facc15",
                status="ACTIVE",
                progress=0,
                briefing="Welcome to the new account infrastructure."
            )
            session.add(m1)

            # --- Budget ---
            budget = BudgetWidget(user_id=user.id, monthly_limit=50000, spent=0, currency="INR")
            session.add(budget)

            # --- Habits ---
            habits = HabitWidget(
                user_id=user.id,
                grid_data=[
                    {"name": "Focus", "history": [0, 0, 0, 0, 0, 0, 0]},
                    {"name": "Health", "history": [0, 0, 0, 0, 0, 0, 0]},
                    {"name": "Sleep", "history": [0, 0, 0, 0, 0, 0, 0]}
                ]
            )
            session.add(habits)

            # --- Scribble ---
            scribble = ScribbleWidget(user_id=user.id, content=f"Hello {email}, your space is ready.")
            session.add(scribble)

            # --- Travel ---
            travel = TravelWidget(
                user_id=user.id,
                places=[
                    {"id": 1, "name": "Dream Destination", "photos": []}
                ]
            )
            session.add(travel)
            
            # --- Tasks ---
            task = TaskWidget(user_id=user.id, content="Set up profile", is_done=False)
            session.add(task)
            
            # --- Notes ---
            note = NoteWidget(user_id=user.id, title="Welcome", content="This is your new persistent space.")
            session.add(note)

            # --- Love Widget ---
            love = LoveWidget(user_id=user.id, name="Favorites", category="misc", description="Add things you love here.", link="#")
            session.add(love)

            # Commit all widgets for this user
            await session.commit()
        
        print(f"✅ ADDITIONAL SEEDING COMPLETE.")

if __name__ == "__main__":
    asyncio.run(seed_additional())