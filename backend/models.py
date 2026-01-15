from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

# --- THE BLOCK PROTOCOL (For Weave & Codex) ---
# This is the "Atomic Unit" of your platform. 
# A Page is a block. A Grid is a block. A Task is a block.
class Block(SQLModel, table=True):
    id: str = Field(primary_key=True)
    type: str = Field(index=True)  # e.g., "page", "grid", "text", "data_source"
    parent_id: Optional[str] = Field(default=None, index=True)
    
    # The "Brain" of the block. Stores text, grid config, or data source IDs.
    properties: Dict = Field(default={}, sa_column=Column(JSON))
    
    # For permissioning and merging logic later
    permissions: Dict = Field(default={}, sa_column=Column(JSON))
    
    # Ordering in the list
    rank: str = Field(default="a") 


# --- THE MARKETING CONTENT MODELS ---
# These store the high-level dossiers for your public site.

class Framework(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    subject: str
    description: str
    
    # Complex nested data stored as JSON
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
    
    # Complex nested data stored as JSON
    hero: Dict = Field(default={}, sa_column=Column(JSON))
    modules: List[Dict] = Field(default=[], sa_column=Column(JSON))
    comparison: Dict = Field(default={}, sa_column=Column(JSON))
    bottomLine: str