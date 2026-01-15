from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime

# --- THE BLOCK PROTOCOL (For Weave & Dynamic Content) ---
class Block(SQLModel, table=True):
    id: str = Field(primary_key=True)
    type: str = Field(index=True)
    parent_id: Optional[str] = Field(default=None, index=True)
    properties: Dict = Field(default={}, sa_column=Column(JSON))
    permissions: Dict = Field(default={}, sa_column=Column(JSON))
    rank: str = Field(default="a")

# --- MARKETING: GLOBAL CONFIG (The Identity) ---
class SiteConfig(SQLModel, table=True):
    id: str = Field(primary_key=True, default="global") # Always "global"
    brand_name: str = Field(default="RESINEN")
    logo_url: str
    contact_email: str
    social_links: Dict = Field(default={}, sa_column=Column(JSON)) # { linkedin: "...", x: "..." }
    footer_text: str
    
    # Navigation Links (Dynamic Menu)
    navigation: List[Dict] = Field(default=[], sa_column=Column(JSON)) 

# --- MARKETING: HOMEPAGE (The Face) ---
class HomePage(SQLModel, table=True):
    id: str = Field(primary_key=True, default="home") # Always "home"
    
    # Hero Section
    hero_title: str
    hero_subtitle: str
    hero_cta_primary: str
    hero_cta_secondary: str
    
    # Featured Content (What shows up in the grid)
    featured_insights: List[str] = Field(default=[], sa_column=Column(JSON)) # List of IDs
    
    # Impact Ticker
    ticker_items: List[Dict] = Field(default=[], sa_column=Column(JSON)) # [{ label: "Yield", value: "98%" }]

# --- MARKETING: BLOG (The Voice) ---
class BlogPost(SQLModel, table=True):
    slug: str = Field(primary_key=True)
    title: str
    summary: str
    cover_image: str
    content: str # Markdown or HTML
    published: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    category: str

class DoctrinePage(SQLModel, table=True):
    id: str = Field(primary_key=True, default="doctrine")
    
    title: str = Field(default="The Doctrine")
    subtitle: str = Field(default="Our core operating principles.")
    
    # The Content
    intro_text: str = Field(sa_column=Column(JSON)) # Rich text or long string
    principles: List[Dict] = Field(default=[], sa_column=Column(JSON)) # [{ title: "Entropy", desc: "..." }]
    
    # Team / Leadership Section
    team_members: List[Dict] = Field(default=[], sa_column=Column(JSON))

# --- MARKETING: CONTACT (The Interface) ---
class ContactPage(SQLModel, table=True):
    id: str = Field(primary_key=True, default="contact")
    
    title: str = Field(default="Initialize Engagement")
    subtitle: str = Field(default="Begin the transmission.")
    
    # Locations
    locations: List[Dict] = Field(default=[], sa_column=Column(JSON)) # [{ city: "Zurich", address: "..." }]
    
    # Form Configuration
    form_success_message: str = Field(default="Transmission received. Stand by.")
    support_email: str = Field(default="help@resinen.com")

# --- EXISTING DOCTRINE MODELS ---
class Framework(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    subject: str
    description: str
    summary: Dict = Field(default={}, sa_column=Column(JSON))
    isomorphism: Dict = Field(default={}, sa_column=Column(JSON))
    nodes: List[Dict] = Field(default=[], sa_column=Column(JSON))
    solution: Dict = Field(default={}, sa_column=Column(JSON))
    formulas: Dict = Field(default={}, sa_column=Column(JSON))
    protocol: Dict = Field(default={}, sa_column=Column(JSON))
    values: Dict = Field(default={}, sa_column=Column(JSON))

class Engine(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    category: str
    description: str
    hero: Dict = Field(default={}, sa_column=Column(JSON))
    modules: List[Dict] = Field(default=[], sa_column=Column(JSON))
    comparison: Dict = Field(default={}, sa_column=Column(JSON))
    bottomLine: str