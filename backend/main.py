from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

# Import our local modules
from database import init_db, get_session
from models import Block, Framework, Engine

app = FastAPI(
    title="Resinen Platform API",
    description="The Neural Backend for Codex (CMS) and Weave (Client OS).",
    version="1.0.0"
)

# --- LIFECYCLE ---
@app.on_event("startup")
def on_startup():
    print("INITIALIZING RESINEN DATABASE...")
    init_db()
    print("SYSTEM ONLINE.")

@app.get("/")
def health_check():
    return {"status": "active", "system": "Resinen Platform V1"}


# ==========================================
#  FRAMEWORK ENDPOINTS (Marketing CMS)
# ==========================================

@app.get("/frameworks", response_model=List[Framework])
def get_frameworks(session: Session = Depends(get_session)):
    return session.exec(select(Framework)).all()

@app.get("/frameworks/{framework_id}", response_model=Framework)
def get_framework(framework_id: str, session: Session = Depends(get_session)):
    framework = session.get(Framework, framework_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework

@app.post("/frameworks", response_model=Framework)
def create_framework(framework: Framework, session: Session = Depends(get_session)):
    # Check if exists
    existing = session.get(Framework, framework.id)
    if existing:
        raise HTTPException(status_code=400, detail="Framework ID already exists")
    
    session.add(framework)
    session.commit()
    session.refresh(framework)
    return framework

@app.put("/frameworks/{framework_id}", response_model=Framework)
def update_framework(framework_id: str, framework_data: Framework, session: Session = Depends(get_session)):
    framework = session.get(Framework, framework_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    # Update fields
    framework_data_dict = framework_data.dict(exclude_unset=True)
    for key, value in framework_data_dict.items():
        setattr(framework, key, value)
        
    session.add(framework)
    session.commit()
    session.refresh(framework)
    return framework


# ==========================================
#  ENGINE ENDPOINTS (Marketing CMS)
# ==========================================

@app.get("/engines", response_model=List[Engine])
def get_engines(session: Session = Depends(get_session)):
    return session.exec(select(Engine)).all()

@app.post("/engines", response_model=Engine)
def create_engine(engine: Engine, session: Session = Depends(get_session)):
    existing = session.get(Engine, engine.id)
    if existing:
        raise HTTPException(status_code=400, detail="Engine ID already exists")
    
    session.add(engine)
    session.commit()
    session.refresh(engine)
    return engine


# ==========================================
#  BLOCK ENDPOINTS (Weave OS)
# ==========================================

@app.get("/blocks", response_model=List[Block])
def get_blocks(parent_id: str = None, session: Session = Depends(get_session)):
    """
    Fetch blocks. If parent_id is provided, fetches children of that block (e.g., items in a grid).
    """
    statement = select(Block)
    if parent_id:
        statement = statement.where(Block.parent_id == parent_id)
    return session.exec(statement).all()

@app.post("/blocks", response_model=Block)
def create_block(block: Block, session: Session = Depends(get_session)):
    session.add(block)
    session.commit()
    session.refresh(block)
    return block

@app.delete("/blocks/{block_id}")
def delete_block(block_id: str, session: Session = Depends(get_session)):
    block = session.get(Block, block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    session.delete(block)
    session.commit()
    return {"ok": True}