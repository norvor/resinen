import asyncio
import random
import logging
from sqlmodel import select
from app.core.database import async_session_factory

# 🏗️ IMPORTS
from app.models.social import Post
from app.models.user import User
from app.models.community import Community

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_engines():
    async with async_session_factory() as session:
        logger.info("⚙️  Seeding Engine Content...")

        # 1. FETCH CONTEXT (User & Community ONLY)
        # We don't look for Chapters anymore.
        
        # Get Admin User
        u_res = await session.exec(select(User).where(User.email == "admin@unionstation.com"))
        user = u_res.first()
        
        # Get Union Station
        c_res = await session.exec(select(Community).where(Community.slug == "union-station"))
        community = c_res.first()

        if not community or not user:
            logger.error("❌ Context Missing: Run 'python -m app.seeder' first!")
            return

        # 2. SEED SOCIAL POSTS (To Community Root)
        logger.info(f"📡 Seeding Social Feed for {community.name} (Root)...")
        
        # Check if we need to seed
        existing = await session.exec(select(Post).where(Post.community_id == community.id))
        
        if len(existing.all()) < 10:
            posts_to_create = []
            
            # Create 50 Posts
            for i in range(50):
                # Bento Grid Layout Randomizer
                media = []
                roll = random.random()
                if roll > 0.8: 
                    media = ["https://picsum.photos/800/600?random=" + str(i)] 
                elif roll > 0.6: 
                    media = ["https://picsum.photos/400/600?random=" + str(i), "https://picsum.photos/400/400?random=" + str(i+100)] 
                elif roll > 0.5: 
                    media = [
                        "https://picsum.photos/800/400?random=" + str(i), 
                        "https://picsum.photos/400/400?random=" + str(i+200),
                        "https://picsum.photos/400/400?random=" + str(i+300)
                    ] 
                
                post = Post(
                    community_id=community.id,
                    author_id=user.id,
                    chapter_id=None, # Explicitly None -> Goes to Community Root Feed
                    
                    title=f"Update #{50-i}",
                    content=f"This is a simulated post number {50-i} in the Main Community Feed. Testing infinite scroll. #Resinen",
                    media_urls=media,
                    like_count=random.randint(0, 500),
                    comment_count=random.randint(0, 50),
                    view_count=random.randint(100, 5000),
                    meta_data={}
                )
                session.add(post)
            
            await session.commit()
            logger.info("✅ Created 50 Social Posts in Community Root.")
        else:
            logger.info("⏭️  Feed already populated. Skipping.")

        logger.info("✅ ENGINE SEED COMPLETE")

if __name__ == "__main__":
    asyncio.run(seed_engines())