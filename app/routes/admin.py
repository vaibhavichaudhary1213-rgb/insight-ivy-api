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

# SIMPLIFIED STATS ENDPOINT FOR TESTING
@router.get("/stats")
async def get_admin_stats(
    authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get admin statistics"""
    print("🔵 /stats endpoint called")
    try:
        # Simple test response
        return {
            "message": "Stats endpoint is working!",
            "timestamp": datetime.utcnow().isoformat(),
            "authenticated": authenticated
        }
    except Exception as e:
        print(f"🔴 Error in stats endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

print("🔵 /stats endpoint registered (simplified version)")

# Add a test endpoint that doesn't need auth
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
    """Track user activity"""
    print(f"🔵 /track/user called for user: {user_id}")
    # ... rest of your existing track_user_activity code ...
    # (keep your existing implementation)
    
    # For brevity, I'm not copying the full implementation here
    # But you should keep your existing code
    
    return {"status": "tracked", "user_id": user_id}

print("🔵 /track/user endpoint registered")
print("🔵 Loading admin.py - END")