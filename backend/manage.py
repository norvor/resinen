import asyncio
import sys
import argparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

# Adjust these imports to match your project structure
# If this script is in the root 'backend' folder, these should work.
from app.core.database import engine
from app.models.user import User

async def promote_user(email: str):
    print(f"🔍 Searching for user: {email}...")
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Find the user
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            print(f"❌ Error: User '{email}' not found.")
            return

        if user.is_superuser:
            print(f"⚠️  User '{email}' is already a Superuser.")
            return

        # Promote
        user.is_superuser = True
        session.add(user)
        await session.commit()
        print(f"✅ SUCCESS: {user.full_name} ({email}) has been promoted to Superuser.")
        print("   You may need to log out and log back in for the token to update.")

async def demote_user(email: str):
    # Same logic but False, good for security management
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            user.is_superuser = False
            session.add(user)
            await session.commit()
            print(f"✅ Revoked Superuser status from {email}")

def main():
    parser = argparse.ArgumentParser(description="Resinen System Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: promote
    p_promote = subparsers.add_parser("promote", help="Promote a user to Superuser")
    p_promote.add_argument("email", help="The email address of the user")

    # Command: demote
    p_demote = subparsers.add_parser("demote", help="Revoke Superuser status")
    p_demote.add_argument("email", help="The email address of the user")

    args = parser.parse_args()

    if args.command == "promote":
        asyncio.run(promote_user(args.email))
    elif args.command == "demote":
        asyncio.run(demote_user(args.email))

if __name__ == "__main__":
    main()