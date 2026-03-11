# app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import secrets
from typing import Optional
from ..database import SessionLocal, User, Activity, Reflection, Goal

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer(auto_error=False)  # Don't auto-error, we'll handle it

# Admin authentication - use environment variable in production!
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # Change this in production!
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", secrets.token_urlsafe(32))

# Store tokens in memory (in production, use Redis or database)
active_tokens = {ADMIN_TOKEN: datetime.utcnow() + timedelta(days=7)}

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Check if token exists and is not expired
    if token not in active_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check expiration
    if active_tokens[token] < datetime.utcnow():
        del active_tokens[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return True

@router.post("/login")
async def admin_login(password: str = Body(..., embed=True)):
    """Login to admin dashboard"""
    if password == ADMIN_PASSWORD:
        # Generate new token or return existing
        return {
            "success": True, 
            "token": ADMIN_TOKEN,
            "expires": active_tokens[ADMIN_TOKEN].isoformat()
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password"
    )

@router.post("/logout")
async def admin_logout(authenticated: bool = Depends(verify_admin)):
    """Logout from admin dashboard"""
    # In a real app, you'd invalidate the specific token
    # For simplicity, we'll just return success
    return {"success": True, "message": "Logged out successfully"}

@router.get("/stats")
async def get_admin_stats(
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get REAL admin statistics from database (protected)"""
    
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
    
    # Get recent reflections (with user info)
    recent_reflections = db.query(
        Reflection, User.name
    ).join(
        User, Reflection.user_id == User.user_id, isouter=True
    ).order_by(
        Reflection.created_at.desc()
    ).limit(10).all()
    
    # Get learning goals (with user info)
    goals = db.query(
        Goal, User.name
    ).join(
        User, Goal.user_id == User.user_id, isouter=True
    ).order_by(
        Goal.created_at.desc()
    ).limit(20).all()
    
    # Calculate total sessions
    total_sessions = db.query(db.func.sum(User.total_sessions)).scalar() or 0
    
    # Get activity breakdown by type
    activity_breakdown = db.query(
        Activity.activity_type, 
        db.func.count(Activity.id).label('count')
    ).group_by(Activity.activity_type).all()
    
    return {
        "uniqueUsers": total_users,
        "activeToday": active_today,
        "activitiesCompleted": total_activities,
        "activitiesToday": activities_today,
        "totalSessions": total_sessions,
        "signups": new_this_week,
        "activityBreakdown": [
            {"type": a[0], "count": a[1]} for a in activity_breakdown
        ],
        "recentReflections": [
            {
                "id": r.Reflection.id,
                "question": r.Reflection.question,
                "answer": r.Reflection.answer[:100] + "..." if len(r.Reflection.answer) > 100 else r.Reflection.answer,
                "date": r.Reflection.created_at.strftime("%b %d, %Y"),
                "time": r.Reflection.created_at.strftime("%I:%M %p"),
                "user_id": r.Reflection.user_id,
                "user_name": r.name or f"User_{r.Reflection.user_id[:8]}"
            } for r in recent_reflections
        ],
        "learningGoals": [
            {
                "id": g.Goal.id,
                "text": g.Goal.text,
                "completed": g.Goal.completed,
                "created_at": g.Goal.created_at.strftime("%b %d, %Y"),
                "user_id": g.Goal.user_id,
                "user_name": g.name or f"User_{g.Goal.user_id[:8]}"
            } for g in goals
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/track/user")
async def track_user_activity(
    user_id: str = Body(..., embed=True),
    activity_type: str = Body(..., embed=True),
    activity_data: dict = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Track user activity in REAL TIME (public endpoint - no auth needed)"""
    
    # Validate input
    if not user_id or not activity_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id and activity_type are required"
        )
    
    # Find or create user
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(
            user_id=user_id, 
            name=f"User_{user_id[:8]}",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.flush()  # Flush to get user.id if needed
    
    # Update user stats
    user.last_active = datetime.utcnow()
    user.total_sessions += 1
    
    # Track activity
    activity = Activity(
        user_id=user_id,
        activity_type=activity_type,
        activity_data=activity_data,
        created_at=datetime.utcnow()
    )
    db.add(activity)
    
    # Handle specific activity types
    if activity_type == "reflection":
        reflection = Reflection(
            user_id=user_id,
            question=activity_data.get("question", "Reflection"),
            answer=activity_data.get("answer", ""),
            created_at=datetime.utcnow()
        )
        db.add(reflection)
        
    elif activity_type == "goal":
        goal = Goal(
            user_id=user_id,
            text=activity_data.get("text", ""),
            completed=activity_data.get("completed", False),
            created_at=datetime.utcnow()
        )
        db.add(goal)
        
    elif activity_type == "mood_message":
        # Just track the mood message, no additional processing needed
        pass
        
    elif activity_type == "signup":
        # New user signup - already handled by user creation
        pass
        
    elif activity_type == "page_view":
        # Track page view without additional processing
        pass
    
    db.commit()
    
    return {
        "status": "tracked", 
        "user_id": user_id,
        "activity_type": activity_type,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/goals")
async def create_goal(
    text: str = Body(..., embed=True),
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new learning goal (admin only)"""
    
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goal text is required"
        )
    
    # Create goal for admin (you might want to associate with a specific admin user)
    goal = Goal(
        user_id="admin",  # Or use a specific admin user ID
        text=text.strip(),
        completed=False,
        created_at=datetime.utcnow()
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    return {
        "success": True,
        "goal": {
            "id": goal.id,
            "text": goal.text,
            "completed": goal.completed,
            "created_at": goal.created_at.isoformat()
        }
    }

@router.post("/goals/{goal_id}/toggle")
async def toggle_goal(
    goal_id: int,
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Toggle goal completion status (admin only)"""
    
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    goal.completed = not goal.completed
    goal.completed_at = datetime.utcnow() if goal.completed else None
    db.commit()
    
    return {
        "success": True,
        "goal": {
            "id": goal.id,
            "text": goal.text,
            "completed": goal.completed
        }
    }

@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: int,
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete a goal (admin only)"""
    
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    db.delete(goal)
    db.commit()
    
    return {"success": True, "message": "Goal deleted"}

@router.get("/export")
async def export_all_data(
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Export all data as JSON (admin only)"""
    
    # Get all users
    users = db.query(User).all()
    
    # Get all activities
    activities = db.query(Activity).order_by(Activity.created_at.desc()).limit(1000).all()
    
    # Get all reflections
    reflections = db.query(Reflection).order_by(Reflection.created_at.desc()).all()
    
    # Get all goals
    goals = db.query(Goal).order_by(Goal.created_at.desc()).all()
    
    return {
        "exported_at": datetime.utcnow().isoformat(),
        "summary": {
            "total_users": len(users),
            "total_activities": len(activities),
            "total_reflections": len(reflections),
            "total_goals": len(goals)
        },
        "users": [
            {
                "user_id": u.user_id,
                "name": u.name,
                "created_at": u.created_at.isoformat(),
                "last_active": u.last_active.isoformat(),
                "total_sessions": u.total_sessions
            } for u in users
        ],
        "recent_activities": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "type": a.activity_type,
                "data": a.activity_data,
                "created_at": a.created_at.isoformat()
            } for a in activities
        ],
        "all_reflections": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "question": r.question,
                "answer": r.answer,
                "created_at": r.created_at.isoformat()
            } for r in reflections
        ],
        "all_goals": [
            {
                "id": g.id,
                "user_id": g.user_id,
                "text": g.text,
                "completed": g.completed,
                "created_at": g.created_at.isoformat(),
                "completed_at": g.completed_at.isoformat() if g.completed_at else None
            } for g in goals
        ]
    }

@router.get("/health")
async def health_check():
    """Health check endpoint (public)"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "IvyInsight Admin API"
    }