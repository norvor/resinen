import asyncio
import random
import logging
from sqlmodel import select
from app.core.database import async_session_factory
from app.models.social import Post
from app.models.user import User
from app.models.community import Community

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_engines():
    async with async_session_factory() as session:
        logger.info("⚙️  Seeding Engine Content...")

        # 1. FETCH CONTEXT (Dynamic Lookup)
        # We find the specific community and user to attribute posts to
        community = (await session.exec(select(Community).where(Community.slug == "union-station"))).first()
        user = (await session.exec(select(User).where(User.email == "admin@unionstation.com"))).first()

        if not community or not user:
            logger.error("❌ Error: Run 'python -m app.seeder' first! User/Community not found.")
            return

        # 2. SEED SOCIAL ENGINE
        logger.info(f"📡 Seeding Social Feed for {community.name}...")
        
        # Check if we already have posts to avoid over-seeding on re-runs
        existing_posts = (await session.exec(select(Post).where(Post.community_id == community.id))).all()
        
        if len(existing_posts) < 10:
            posts_to_create = []
            
            # Generate 50 Posts
            for i in range(50):
                # Randomized Layout Logic (Bento Grid)
                media = []
                roll = random.random()
                if roll > 0.8: 
                    media = ["https://picsum.photos/800/600?random=" + str(i)] # Single
                elif roll > 0.6: 
                    media = ["https://picsum.photos/400/600?random=" + str(i), "https://picsum.photos/400/400?random=" + str(i+100)] # Split
                elif roll > 0.5: 
                    media = [
                        "https://picsum.photos/800/400?random=" + str(i), 
                        "https://picsum.photos/400/400?random=" + str(i+200),
                        "https://picsum.photos/400/400?random=" + str(i+300)
                    ] # Magazine
                
                post = Post(
                    community_id=community.id,
                    author_id=user.id,
                    title=f"Update #{50-i}",
                    content=f"This is a simulated post number {50-i} to test the infinite scroll and bento grid layout. #Resinen",
                    media_urls=media,
                    like_count=random.randint(0, 500),
                    comment_count=random.randint(0, 50),
                    view_count=random.randint(100, 5000)
                )
                session.add(post)
            
            await session.commit()
            logger.info("✅ Created 50 Social Posts.")
        else:
            logger.info("⏭️  Social Feed already populated. Skipping.")

        # 3. FUTURE ENGINES (Placeholders)
        # When we build Arena/Bazaar, add their seeding logic here.
        
        logger.info("✅ ENGINE SEED COMPLETE")

if __name__ == "__main__":
    asyncio.run(seed_engines())