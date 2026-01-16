from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from database import init_db, get_session
from fastapi.middleware.cors import CORSMiddleware
from models import Journey, Stop, UserProgress

# --- CRITICAL FIX: Import this to load relationships ---
from sqlalchemy.orm import selectinload 

app = FastAPI(title="Life Maintenance Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def health_check():
    return {"status": "active", "mode": "Life Maintenance"}

# --- HELPER: GET USER ---
def get_current_user_progress(session: Session) -> UserProgress:
    user = session.get(UserProgress, "me")
    if not user:
        user = UserProgress(
            id="me", 
            active_journey_id="farming", 
            current_stop_index=0,
            daily_care_points=0,
            last_care_date=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    if user.last_care_date.date() < datetime.utcnow().date():
        user.daily_care_points = 0
        user.last_care_date = datetime.utcnow()
        session.add(user)
        session.commit()
        session.refresh(user)

    return user

# --- GAMEPLAY ENDPOINTS ---
@app.get("/status", response_model=UserProgress)
def get_status(session: Session = Depends(get_session)):
    return get_current_user_progress(session)

@app.post("/care")
def submit_care_action(session: Session = Depends(get_session)):
    user = get_current_user_progress(session)
    user.last_care_date = datetime.utcnow()
    user.daily_care_points += 1
    
    did_level_up = False
    if user.daily_care_points >= 5:
        user.current_stop_index += 1
        user.daily_care_points = 0 
        did_level_up = True

    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "status": "success",
        "daily_points": user.daily_care_points,
        "current_stop": user.current_stop_index,
        "leveled_up": did_level_up
    }

# --- CMS ENDPOINTS ---

@app.get("/journeys", response_model=list[Journey])
def get_journeys(session: Session = Depends(get_session)):
    # FIXED: We use .options(selectinload(...)) to ensure 'stops' are included
    statement = select(Journey).options(selectinload(Journey.stops))
    return session.exec(statement).all()

@app.post("/journeys", response_model=Journey)
def create_journey(journey: Journey, session: Session = Depends(get_session)):
    session.merge(journey)
    session.commit()
    return journey

@app.post("/stops", response_model=Stop)
def create_stop(stop: Stop, session: Session = Depends(get_session)):
    session.merge(stop)
    session.commit()
    return stop