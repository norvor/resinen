import math
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.reputation import ReputationEvent

# CONFIG
XP_PER_LIKE = 10
XP_PER_JURY_VOTE = 50
XP_PER_COMMENT = 2

async def award_xp(user_id: str, amount: int, source: str, source_id: str, db: AsyncSession):
    # 1. Log the Event
    event = ReputationEvent(
        user_id=user_id,
        xp_amount=amount,
        source=source,
        source_id=str(source_id)
    )
    db.add(event)
    
    # 2. Update User Stats
    user = await db.get(User, user_id)
    if not user:
        return
        
    user.xp += amount
    user.reputation_score += amount # Reputation might differ from XP later, but for now they are synced
    
    # 3. Level Up Logic (Simple RPG Curve)
    # Level 1 = 0 XP
    # Level 2 = 100 XP
    # Level 3 = 400 XP
    # Level 10 = 10,000 XP
    new_level = int(math.sqrt(user.xp) * 0.1) + 1
    
    if new_level > user.level:
        user.level = new_level
        # Trigger Notification: "LEVEL UP!" (Future)
        
    db.add(user)
    await db.commit()
    return user.level