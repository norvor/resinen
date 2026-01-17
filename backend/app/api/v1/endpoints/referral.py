from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from uuid import UUID

from app.api import deps
from app.models.referral import MemberService, Vouch
from app.models.community import Community
from app.models.user import User
from app.schemas.referral import ServiceCreate, ServiceRead, VouchCreate, VouchRead

router = APIRouter()

# --- SERVICES ---

@router.get("/services/", response_model=List[ServiceRead])
async def list_services(
    community_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(deps.get_db),
):
    # Fetch services ordered by Reputation (Highest Vouch Count first)
    query = (
        select(MemberService)
        .where(MemberService.community_id == community_id)
        .order_by(desc(MemberService.vouch_count))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/services/", response_model=ServiceRead)
async def create_service(
    *,
    db: AsyncSession = Depends(deps.get_db),
    service_in: ServiceCreate,
    current_user: User = Depends(deps.get_current_user),
):
    # Verify Community
    community = await db.get(Community, service_in.community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
        
    service = MemberService(
        **service_in.dict(),
        user_id=current_user.id
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service

# --- VOUCHING ---

@router.post("/services/{service_id}/vouch", response_model=VouchRead)
async def vouch_for_service(
    service_id: UUID,
    vouch_in: VouchCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. Fetch Service
    service = await db.get(MemberService, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service listing not found")
        
    # 2. Prevent Self-Vouching
    if service.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot vouch for yourself")
        
    # 3. Check if already vouched (One vouch per user per service)
    existing_vouch = await db.execute(
        select(Vouch).where(
            Vouch.service_id == service_id,
            Vouch.voucher_id == current_user.id
        )
    )
    if existing_vouch.scalars().first():
        raise HTTPException(status_code=400, detail="You have already vouched for this service")
        
    # 4. Create Vouch
    vouch = Vouch(
        service_id=service_id,
        voucher_id=current_user.id,
        comment=vouch_in.comment
    )
    
    # 5. Increment Reputation Score
    service.vouch_count += 1
    
    db.add(vouch)
    db.add(service) # Save the new count
    await db.commit()
    await db.refresh(vouch)
    
    return vouch