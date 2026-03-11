# app/routes/admin.py
print("🔵 Loading admin.py - START")
print(f"🔵 __name__: {__name__}")

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import secrets
from typing import Optional

print("🔵 Imports completed")

# Database import - this might be failing
try:
    from ..database import SessionLocal, User, Activity, Reflection, Goal
    print("🔵 Database imports successful")
    print(f"🔵 User model: {User}")
except Exception as e:
    print(f"🔴 Database import ERROR: {e}")
    raise

print("🔵 Creating router")
router = APIRouter(prefix="/admin", tags=["admin"])
print(f"🔵 Router created with prefix: {router.prefix}")

security = HTTPBearer(auto_error=False)

# Admin authentication
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", secrets.token_urlsafe(32))

print(f"🔵 ADMIN_TOKEN generated: {ADMIN_TOKEN[:10]}...")

# Store tokens in memory
active_tokens = {ADMIN_TOKEN: datetime.utcnow() + timedelta(days=7)}
print(f"🔵 active_tokens initialized")

# Dependency to get DB session
def get_db():
    print("🔵 get_db called")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        print("🔵 db closed")

print("🔵 get_db function defined")

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token"""
    print(f"🔵 verify_admin called with credentials: {credentials is not None}")
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    print(f"🔵 Token received: {token[:10]}...")
    
    if token not in active_tokens:
        print(f"🔴 Token not found in active_tokens")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if active_tokens[token] < datetime.utcnow():
        print(f"🔴 Token expired")
        del active_tokens[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"🔵 Token valid")
    return True

print("🔵 verify_admin function defined")

@router.post("/login")
async def admin_login(password: str = Body(..., embed=True)):
    """Login to admin dashboard"""
    print(f"🔵 Login attempt")
    if password == ADMIN_PASSWORD:
        return {
            "success": True, 
            "token": ADMIN_TOKEN,
            "expires": active_tokens[ADMIN_TOKEN].isoformat()
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password"
    )

print("🔵 /login endpoint registered")

@router.post("/logout")
async def admin_logout(authenticated: bool = Depends(verify_admin)):
    """Logout from admin dashboard"""
    return {"success": True, "message": "Logged out successfully"}

print("🔵 /logout endpoint registered")

# FULL STATS ENDPOINT IMPLEMENTATION
@router.get("/stats")
async def get_admin_stats(
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get REAL admin statistics from database (protected)"""
    print("🔵 /stats endpoint called with full implementation")
    
    try:
        # Count total unique users
        total_users = db.query(User).count()
        print(f"🔵 Total users: {total_users}")
        
        # Count users active in last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        active_today = db.query(User).filter(User.last_active >= yesterday).count()
        print(f"🔵 Active today: {active_today}")
        
        # Count new users this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_this_week = db.query(User).filter(User.created_at >= week_ago).count()
        print(f"🔵 New this week: {new_this_week}")
        
        # Count total activities
        total_activities = db.query(Activity).count()
        print(f"🔵 Total activities: {total_activities}")
        
        # Count activities today
        activities_today = db.query(Activity).filter(Activity.created_at >= yesterday).count()
        print(f"🔵 Activities today: {activities_today}")
        
        # Get recent reflections (with user info)
        recent_reflections = db.query(
            Reflection, User.name
        ).join(
            User, Reflection.user_id == User.user_id, isouter=True
        ).order_by(
            Reflection.created_at.desc()
        ).limit(10).all()
        print(f"🔵 Recent reflections count: {len(recent_reflections)}")
        
        # Get learning goals (with user info)
        goals = db.query(
            Goal, User.name
        ).join(
            User, Goal.user_id == User.user_id, isouter=True
        ).order_by(
            Goal.created_at.desc()
        ).limit(20).all()
        print(f"🔵 Goals count: {len(goals)}")
        
        # Calculate total sessions
        total_sessions = db.query(db.func.sum(User.total_sessions)).scalar() or 0
        print(f"🔵 Total sessions: {total_sessions}")
        
        # Get activity breakdown by type
        activity_breakdown = db.query(
            Activity.activity_type, 
            db.func.count(Activity.id).label('count')
        ).group_by(Activity.activity_type).all()
        print(f"🔵 Activity breakdown: {activity_breakdown}")
        
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
    except Exception as e:
        print(f"🔴 Error in stats endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

print("🔵 /stats endpoint registered (full implementation)")

# Test endpoint that doesn't need auth
@router.get("/ping")
async def ping():
    """Simple test endpoint"""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

print("🔵 /ping endpoint registered")

@router.post("/track/user")
async def track_user_activity(
    user_id: str = Body(..., embed=True),
    activity_type: str = Body(..., embed=True),
    activity_data: dict = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Track user activity in REAL TIME (public endpoint - no auth needed)"""
    print(f"🔵 /track/user called for user: {user_id}, type: {activity_type}")
    
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
        db.flush()
        print(f"🔵 Created new user: {user_id}")
    
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
        print(f"🔵 Added reflection for user: {user_id}")
        
    elif activity_type == "goal":
        goal = Goal(
            user_id=user_id,
            text=activity_data.get("text", ""),
            completed=activity_data.get("completed", False),
            created_at=datetime.utcnow()
        )
        db.add(goal)
        print(f"🔵 Added goal for user: {user_id}")
        
    elif activity_type == "mood_message":
        print(f"🔵 Tracked mood message for user: {user_id}")
        
    elif activity_type == "signup":
        print(f"🔵 Tracked signup for user: {user_id}")
        
    elif activity_type == "page_view":
        print(f"🔵 Tracked page view for user: {user_id}")
    
    db.commit()
    print(f"🔵 Database committed for user: {user_id}")
    
    return {
        "status": "tracked", 
        "user_id": user_id,
        "activity_type": activity_type,
        "timestamp": datetime.utcnow().isoformat()
    }

print("🔵 /track/user endpoint registered")

@router.post("/goals")
async def create_goal(
    text: str = Body(..., embed=True),
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new learning goal (admin only)"""
    print(f"🔵 /goals POST called with text: {text[:20]}...")
    
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goal text is required"
        )
    
    goal = Goal(
        user_id="admin",
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

print("🔵 /goals POST endpoint registered")

@router.post("/goals/{goal_id}/toggle")
async def toggle_goal(
    goal_id: int,
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Toggle goal completion status (admin only)"""
    print(f"🔵 /goals/{goal_id}/toggle called")
    
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

print("🔵 /goals/toggle endpoint registered")

@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: int,
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete a goal (admin only)"""
    print(f"🔵 /goals/{goal_id} DELETE called")
    
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    db.delete(goal)
    db.commit()
    
    return {"success": True, "message": "Goal deleted"}

print("🔵 /goals DELETE endpoint registered")

@router.get("/export")
async def export_all_data(
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Export all data as JSON (admin only)"""
    print("🔵 /export called")
    
    # Get all users
    users = db.query(User).all()
    
    # Get all activities (limited to 1000 for performance)
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

print("🔵 /export endpoint registered")

@router.get("/health")
async def health_check():
    """Health check endpoint (public)"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "IvyInsight Admin API"
    }

print("🔵 /health endpoint registered")
print("🔵 Loading admin.py - END")