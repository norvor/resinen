from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.engine import CommunityEngine
from fastapi import HTTPException

async def summon_jury(community_id: str, issue_id: str, db: AsyncSession):
    # 1. Fetch Community Bylaws to see how many jurors we need
    # We assume the engine key is 'governance'
    stmt = select(CommunityEngine).where(
        CommunityEngine.community_id == community_id,
        CommunityEngine.engine_id == (select(Engine.id).where(Engine.key == "governance"))
    )
    result = await db.execute(stmt)
    link = result.scalars().first()
    
    # Default to 5 jurors if no config found
    jury_size = link.config.get("jury_size", 5) if link else 5
    min_rep = link.config.get("min_rep_for_jury", 50) if link else 50
    
    # 2. Select Random High-Reputation Users
    # Logic: Must be in same community, have rep > X, and NOT be the accused (omitted for brevity)
    juror_query = (
        select(User)
        .where(User.community_id == community_id)
        .where(User.reputation_score >= min_rep)
        .order_by(func.random())
        .limit(jury_size)
    )
    
    jurors = await db.execute(juror_query)
    selected_jurors = jurors.scalars().all()
    
    if not selected_jurors:
        raise HTTPException(status_code=400, detail="Not enough eligible jurors in this community.")

    # 3. Create 'Pending' Votes for them (Summons)
    # In a real app, you would also trigger a Notification here
    from app.models.governance import GovernanceVote
    
    created_votes = []
    for juror in selected_jurors:
        vote_ticket = GovernanceVote(
            issue_id=issue_id,
            user_id=juror.id,
            vote="pending", # Special status indicating they need to vote
            reason="Jury Summons"
        )
        db.add(vote_ticket)
        created_votes.append(vote_ticket)
        
    await db.commit()
    return created_votes