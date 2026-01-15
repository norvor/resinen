from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from database import init_db, get_session
from models import (
    Block, Framework, Engine, 
    SiteConfig, HomePage, BlogPost, 
    DoctrinePage, ContactPage
)
app = FastAPI(title="Resinen Platform API")
app.add_middleware(
    CORSMiddleware,
    # ALLOW_ORIGINS: Who is allowed to talk to this API?
    # For development, allow ALL ("*").
    # For production, you can list specific domains: ["https://resinen.com", "https://cms.resinen.com"]
    allow_origins=["*"], 
    
    allow_credentials=True,
    allow_methods=["*"], # Allow GET, POST, DELETE, etc.
    allow_headers=["*"], # Allow all headers (Content-Type, Authorization, etc.)
)
@app.on_event("startup")
def on_startup():
    init_db()



@app.get("/")
def health_check():
    return {"status": "active"}

# --- SITE CONFIG (SINGLETON) ---
@app.get("/config", response_model=SiteConfig)
def get_config(session: Session = Depends(get_session)):
    config = session.get(SiteConfig, "global")
    if not config:
        # Create default if not exists
        config = SiteConfig(
            id="global", 
            logo_url="/logo.svg", 
            contact_email="contact@resinen.com",
            footer_text="Architects of Entropy Reduction."
        )
        session.add(config)
        session.commit()
    return config

@app.post("/config", response_model=SiteConfig)
def update_config(data: SiteConfig, session: Session = Depends(get_session)):
    data.id = "global" # Force singleton
    session.merge(data)
    session.commit()
    return data

# --- HOMEPAGE (SINGLETON) ---
@app.get("/homepage", response_model=HomePage)
def get_homepage(session: Session = Depends(get_session)):
    home = session.get(HomePage, "home")
    if not home:
        home = HomePage(
            id="home",
            hero_title="Default Title",
            hero_subtitle="Default Subtitle",
            hero_cta_primary="Explore",
            hero_cta_secondary="Contact"
        )
        session.add(home)
        session.commit()
    return home

@app.post("/homepage", response_model=HomePage)
def update_homepage(data: HomePage, session: Session = Depends(get_session)):
    data.id = "home"
    session.merge(data)
    session.commit()
    return data

# --- BLOG POSTS ---
@app.get("/posts", response_model=List[BlogPost])
def get_posts(session: Session = Depends(get_session)):
    return session.exec(select(BlogPost).order_by(BlogPost.created_at.desc())).all()

@app.get("/posts/{slug}", response_model=BlogPost)
def get_post(slug: str, session: Session = Depends(get_session)):
    post = session.get(BlogPost, slug)
    if not post:
        raise HTTPException(404, "Post not found")
    return post

@app.post("/posts", response_model=BlogPost)
def create_post(post: BlogPost, session: Session = Depends(get_session)):
    session.merge(post) # Merge allows create or update based on slug
    session.commit()
    session.refresh(post)
    return post

@app.delete("/posts/{slug}")
def delete_post(slug: str, session: Session = Depends(get_session)):
    post = session.get(BlogPost, slug)
    if post:
        session.delete(post)
        session.commit()
    return {"ok": True}

# --- EXISTING FRAMEWORKS & ENGINES ---
@app.get("/frameworks", response_model=List[Framework])
def get_frameworks(session: Session = Depends(get_session)):
    return session.exec(select(Framework)).all()

@app.post("/frameworks", response_model=Framework)
def create_framework(data: Framework, session: Session = Depends(get_session)):
    session.merge(data)
    session.commit()
    return data

@app.get("/engines", response_model=List[Engine])
def get_engines(session: Session = Depends(get_session)):
    return session.exec(select(Engine)).all()

@app.post("/engines", response_model=Engine)
def create_engine(data: Engine, session: Session = Depends(get_session)):
    session.merge(data)
    session.commit()
    return data

@app.get("/doctrine", response_model=DoctrinePage)
def get_doctrine(session: Session = Depends(get_session)):
    page = session.get(DoctrinePage, "doctrine")
    if not page:
        page = DoctrinePage(
            intro_text="We believe in entropy reduction...",
            principles=[{"title": "Velocity", "desc": "Speed with direction."}]
        )
        session.add(page)
        session.commit()
    return page

@app.post("/doctrine", response_model=DoctrinePage)
def update_doctrine(data: DoctrinePage, session: Session = Depends(get_session)):
    data.id = "doctrine"
    session.merge(data)
    session.commit()
    return data

# --- CONTACT ---
@app.get("/contact", response_model=ContactPage)
def get_contact(session: Session = Depends(get_session)):
    page = session.get(ContactPage, "contact")
    if not page:
        page = ContactPage(
            locations=[{"city": "Zurich", "address": "Prime Tower, Level 5"}]
        )
        session.add(page)
        session.commit()
    return page

@app.post("/contact", response_model=ContactPage)
def update_contact(data: ContactPage, session: Session = Depends(get_session)):
    data.id = "contact"
    session.merge(data)
    session.commit()
    return data