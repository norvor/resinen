from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from database import init_db, get_session
from fastapi.middleware.cors import CORSMiddleware
from models import Journey, Stop, UserProgress, SiteConfig

app = FastAPI(title="Life Maintenance Tool")

# --- CORS: Allow your frontend to talk to this backend ---
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

# --- HELPER: GET CURRENT USER ---
def get_current_user_progress(session: Session) -> UserProgress:
    """
    Fetches the single user 'me'. 
    Resets daily counter if it's a new day.
    """
    user = session.get(UserProgress, "me")
    
    if not user:
        # Initialize the user if they don't exist
        # Defaulting to 'farming' journey for now
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

    # CHECK FOR NEW DAY
    # If the last care date was yesterday (or earlier), reset the counter.
    if user.last_care_date.date() < datetime.utcnow().date():
        user.daily_care_points = 0
        user.last_care_date = datetime.utcnow()
        session.add(user)
        session.commit()
        session.refresh(user)

    return user

# --- ENDPOINTS ---

@app.get("/status", response_model=UserProgress)
def get_status(session: Session = Depends(get_session)):
    """
    Frontend calls this to see:
    1. How many points today (0-5)
    2. Which stop index they are at.
    """
    return get_current_user_progress(session)

@app.post("/care")
def submit_care_action(session: Session = Depends(get_session)):
    """
    The main button press. 
    Logic: 
    - Increment daily points.
    - If points hit 5, move to next Stop and reset points.
    """
    user = get_current_user_progress(session)

    # 1. Update Date to Now
    user.last_care_date = datetime.utcnow()

    # 2. Increment Progress
    user.daily_care_points += 1
    
    did_level_up = False

    # 3. Check for "Stop Completion" (The 5x Rule)
    if user.daily_care_points >= 5:
        user.current_stop_index += 1
        user.daily_care_points = 0 # Reset for the next cycle
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

# --- JOURNEY MANAGEMENT (For your CMS) ---

@app.get("/journeys", response_model=list[Journey])
def get_journeys(session: Session = Depends(get_session)):
    return session.exec(select(Journey)).all()

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