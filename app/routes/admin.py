# app/routes/admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import SessionLocal, User, Activity, Reflection, Goal

router = APIRouter(prefix="/admin", tags=["admin"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    """Get REAL admin statistics from database"""
    
    # Count total unique users
    total_users = db.query(User).count()
    
    # Count users active in last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    active_today = db.query(User).filter(User.last_active >= yesterday).count()
    
    # Count new users this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_this_week = db.query(User).filter(User.created_at >= week_ago).count()
    
    # Count total activities
    total_activities = db.query(Activity).count()
    
    # Count activities today
    activities_today = db.query(Activity).filter(Activity.created_at >= yesterday).count()
    
    # Get recent reflections
    recent_reflections = db.query(Reflection).order_by(
        Reflection.created_at.desc()
    ).limit(5).all()
    
    # Get learning goals
    goals = db.query(Goal).limit(10).all()
    
    # Calculate total sessions
    total_sessions = db.query(db.func.sum(User.total_sessions)).scalar() or 0
    
    return {
        "uniqueUsers": total_users,
        "activeToday": active_today,
        "activitiesCompleted": total_activities,
        "activitiesToday": activities_today,
        "totalSessions": total_sessions,
        "signups": new_this_week,
        "recentReflections": [
            {
                "question": r.question,
                "answer": r.answer,
                "date": r.created_at.strftime("%b %-d"),
                "user_id": r.user_id
            } for r in recent_reflections
        ],
        "learningGoals": [
            {
                "text": g.text,
                "completed": g.completed
            } for g in goals
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/track/user")
async def track_user_activity(
    user_id: str,
    activity_type: str,
    activity_data: dict,
    db: Session = Depends(get_db)
):
    """Track user activity in REAL TIME"""
    
    # Find or create user
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(user_id=user_id, name=f"User_{user_id[:8]}")
        db.add(user)
    
    # Update user stats
    user.last_active = datetime.utcnow()
    user.total_sessions += 1
    
    # Track activity
    activity = Activity(
        user_id=user_id,
        activity_type=activity_type,
        activity_data=activity_data
    )
    db.add(activity)
    
    # If it's a reflection, save it
    if activity_type == "reflection":
        reflection = Reflection(
            user_id=user_id,
            question=activity_data.get("question"),
            answer=activity_data.get("answer")
        )
        db.add(reflection)
    
    # If it's a goal update
    if activity_type == "goal":
        goal = Goal(
            user_id=user_id,
            text=activity_data.get("text"),
            completed=activity_data.get("completed", False)
        )
        db.add(goal)
    
    db.commit()
    
    return {"status": "tracked", "user_id": user_id}