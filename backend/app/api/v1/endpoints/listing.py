from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from urllib.parse import urlparse

from app.core.database import get_session
from app.models.user import User
from app.models.listing import Listing, ListingVouch
from app.schemas.listing import ListingCreate, ListingRead, ListingUpdate
from app.api.deps import get_current_user

router = APIRouter()

# --- HELPER: Extract Domain ---
def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove 'www.' if present for cleaner UI
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return "external-link.com"

# --- 1. GET ALL LISTINGS (Filtered by Community) ---
@router.get("/", response_model=List[ListingRead])
async def read_listings(
    community_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_session)
):
    statement = (
        select(Listing)
        .where(Listing.community_id == community_id)
        .order_by(Listing.vouch_count.desc()) # Show most trusted items first
        .offset(skip)
        .limit(limit)
    )
    listings = await db.exec(statement)
    results = listings.all()

    # Manually populate curator info (Simple Join alternative)
    # Ideally, we would use a joinedload query, but this is fast enough for <100 items
    enriched_results = []
    for item in results:
        # We assume the user is loaded via relationship or lazy loading
        # If using Async SQLModel, we might need an explicit load. 
        # For this sprint, let's trust the Relationship loading or fix if null.
        item.curator_name = item.curator.full_name if item.curator else "Unknown"
        item.curator_avatar = item.curator.avatar_url if item.curator else None
        enriched_results.append(item)
        
    return enriched_results

# --- 2. CREATE LISTING ---
@router.post("/", response_model=ListingRead)
async def create_listing(
    listing_in: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # 1. Auto-extract domain
    domain_str = extract_domain(listing_in.link_url)
    
    # 2. Create Object
    new_listing = Listing(
        **listing_in.dict(),
        curator_id=current_user.id,
        domain=domain_str,
        vouch_count=0
    )
    
    db.add(new_listing)
    await db.commit()
    await db.refresh(new_listing)
    
    # Populate return data
    new_listing.curator_name = current_user.full_name
    new_listing.curator_avatar = current_user.avatar_url
    
    return new_listing

# --- 3. VOUCH (UPVOTE) ---
@router.post("/{listing_id}/vouch", response_model=Any)
async def vouch_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # 1. Check if item exists
    listing = await db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Item not found")

    # 2. Check if already vouched
    existing_vouch = await db.get(ListingVouch, (current_user.id, listing_id))
    
    if existing_vouch:
        # Toggle OFF (Un-vouch)
        await db.delete(existing_vouch)
        listing.vouch_count = max(0, listing.vouch_count - 1)
        action = "removed"
    else:
        # Toggle ON (Vouch)
        new_vouch = ListingVouch(user_id=current_user.id, listing_id=listing_id)
        db.add(new_vouch)
        listing.vouch_count += 1
        action = "added"

    db.add(listing)
    await db.commit()
    
    return {"status": "success", "action": action, "vouch_count": listing.vouch_count}