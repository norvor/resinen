from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from database import init_db, get_session
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Import the new Resinen models
from models import Community, Chapter, User, Membership

app = FastAPI(title="Resinen API")

# CORS - Allowing your CMS and App to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to ["https://codex.resinen.com", "https://app.resinen.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # This creates tables if they don't exist.
    # IMPORTANT: Since we changed models, you might need to drop old tables manually first.
    init_db()

@app.get("/")
def health_check():
    return {"status": "active", "system": "Resinen Core V1"}

# --- COMMUNITY ENDPOINTS ---

@app.post("/communities/", response_model=Community)
def create_community(community: Community, session: Session = Depends(get_session)):
    try:
        session.add(community)
        session.commit()
        session.refresh(community)
        return community
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/communities/", response_model=List[Community])
def list_communities(session: Session = Depends(get_session)):
    return session.exec(select(Community)).all()

@app.get("/communities/{slug}")
def get_community_context(slug: str, session: Session = Depends(get_session)):
    community = session.exec(select(Community).where(Community.slug == slug)).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    return community