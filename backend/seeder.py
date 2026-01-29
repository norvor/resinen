import asyncio
from sqlmodel import SQLModel, select
from sqlalchemy import text
from app.database import engine, init_db, async_session_factory
from app.models import (
    User, BudgetWidget, HabitWidget, ScribbleWidget, TravelWidget, 
    TaskWidget, NoteWidget, LoveWidget, TransmissionWidget, Mission
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_db():
    """
    NUCLEAR OPTION: Drops tables using CASCADE to ignore dependencies.
    """
    print("☢️  INITIATING CORE RESET...")
    async with engine.begin() as conn:
        # We manually drop tables with CASCADE to bypass Foreign Key checks
        # The order doesn't matter when using CASCADE, but we list them all to be safe.
        tables = [
            "transmission_widget", "love_widget", "note_widget", "task_widget",
            "travel_widget", "scribble_widget", "habit_widget", "budget_widget",
            "article", "user", "mission"
        ]
        
        for t in tables:
            # "IF EXISTS" prevents errors if the DB is already empty
            await conn.execute(text(f'DROP TABLE IF EXISTS "{t}" CASCADE;'))
            
    print("✅ CORE WIPED.")

async def seed():
    # 1. Force Clean
    await reset_db()
    
    # 2. Re-Initialize Tables
    await init_db()

    async with async_session_factory() as session:
        print("🌱 Seeding User Data...")
        
        # Create Premium User
        user = User(
            email="premium@resinen.com",
            hashed_password=pwd_context.hash("password123"),
            is_premium=True,
            country_code="IN"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        print("🚀 Initializing Mission Control...")
        m1 = Mission(
            user_id=user.id,
            codename="OPERATION: DAYBREAK",
            rune="🌅",
            color="#facc15",
            status="ACTIVE",
            progress=35,
            briefing="Establish the primary infrastructure for the new platform."
        )
        session.add(m1)

        m2 = Mission(
            user_id=user.id,
            codename="PROJECT: NEON",
            rune="⚡",
            color="#2dd4bf",
            status="STEALTH",
            progress=10,
            briefing="Research phase for the advanced AI integration."
        )
        session.add(m2)

        await session.commit()
        
        # Create Default Widgets
        budget = BudgetWidget(user_id=user.id, monthly_limit=60000, spent=12500, currency="INR")
        session.add(budget)

        habits = HabitWidget(
            user_id=user.id,
            grid_data=[
                {"name": "Deep Work", "history": [1, 1, 1, 0, 1, 1, 1]},
                {"name": "Workout", "history": [0, 1, 1, 1, 0, 1, 0]},
                {"name": "Reading", "history": [1, 0, 0, 1, 1, 1, 1]}
            ]
        )
        session.add(habits)

        scribble = ScribbleWidget(user_id=user.id, content="System initialized. Ready for input.")
        session.add(scribble)

        # THIS WAS THE FIX: 'places' attribute
        travel = TravelWidget(
            user_id=user.id,
            places=[
                {"id": 1, "name": "Kyoto, Japan", "photos": []},
                {"id": 2, "name": "Reykjavik, Iceland", "photos": []}
            ]
        )
        session.add(travel)
        
        # THIS WAS THE FIX: 'content' attribute
        task = TaskWidget(user_id=user.id, content="Deploy Resinen V2", is_done=False)
        session.add(task)
        
        note = NoteWidget(user_id=user.id, title="Manifesto", content="We build for the quiet hours.")
        session.add(note)

        love = LoveWidget(user_id=user.id, name="Dune", category="book", description="Fear is the mind killer.", link="https://google.com")
        session.add(love)

        await session.commit()
        print(f"✅ SEED COMPLETE: User 'premium@resinen.com' created with ID {user.id}")

if __name__ == "__main__":
    asyncio.run(seed())