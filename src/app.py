"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
Now with persistent SQL database backend.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from database import init_db, get_db
from models import Activity, Participant, activity_participants

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.on_event("startup")
def startup_event():
    """Initialize database and seed with sample data on startup."""
    init_db()
    
    # Seed database with sample activities if empty
    db = next(get_db())
    existing_activities = db.query(Activity).count()
    
    if existing_activities == 0:
        # Sample activities data
        sample_activities = [
            {
                "name": "Chess Club",
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
            },
            {
                "name": "Programming Class",
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
            },
            {
                "name": "Gym Class",
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30,
                "participants": ["john@mergington.edu", "olivia@mergington.edu"]
            },
            {
                "name": "Soccer Team",
                "description": "Join the school soccer team and compete in matches",
                "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 22,
                "participants": ["liam@mergington.edu", "noah@mergington.edu"]
            },
            {
                "name": "Basketball Team",
                "description": "Practice and play basketball with the school team",
                "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 15,
                "participants": ["ava@mergington.edu", "mia@mergington.edu"]
            },
            {
                "name": "Art Club",
                "description": "Explore your creativity through painting and drawing",
                "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                "max_participants": 15,
                "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
            },
            {
                "name": "Drama Club",
                "description": "Act, direct, and produce plays and performances",
                "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                "max_participants": 20,
                "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
            },
            {
                "name": "Math Club",
                "description": "Solve challenging problems and participate in math competitions",
                "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
                "max_participants": 10,
                "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
            },
            {
                "name": "Debate Team",
                "description": "Develop public speaking and argumentation skills",
                "schedule": "Fridays, 4:00 PM - 5:30 PM",
                "max_participants": 12,
                "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
            }
        ]
        
        # Create activities with participants
        for activity_data in sample_activities:
            participants_emails = activity_data.pop("participants")
            activity = Activity(**activity_data)
            
            # Add or get participants
            for email in participants_emails:
                participant = db.query(Participant).filter(Participant.email == email).first()
                if not participant:
                    participant = Participant(email=email)
                    db.add(participant)
                activity.participants.append(participant)
            
            db.add(activity)
        
        db.commit()
        db.close()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with participant information."""
    activities = db.query(Activity).all()
    return [activity.to_dict() for activity in activities]


@app.get("/activities/{activity_name}")
def get_activity(activity_name: str, db: Session = Depends(get_db)):
    """Get details of a specific activity."""
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity.to_dict()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity."""
    # Get or create activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get or create participant
    participant = db.query(Participant).filter(Participant.email == email).first()
    if not participant:
        participant = Participant(email=email)
        db.add(participant)
        db.flush()
    
    # Check if already signed up
    if participant in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Check capacity
    if len(activity.participants) >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is at full capacity"
        )
    
    # Add participant to activity
    activity.participants.append(participant)
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity."""
    # Get activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get participant
    participant = db.query(Participant).filter(Participant.email == email).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # Check if signed up
    if participant not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Remove participant from activity
    activity.participants.remove(participant)
    db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.get("/participants")
def get_all_participants(db: Session = Depends(get_db)):
    """Get all registered participants."""
    participants = db.query(Participant).all()
    return [participant.to_dict() for participant in participants]


@app.get("/participants/{email}")
def get_participant(email: str, db: Session = Depends(get_db)):
    """Get details of a specific participant."""
    participant = db.query(Participant).filter(Participant.email == email).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant.to_dict()