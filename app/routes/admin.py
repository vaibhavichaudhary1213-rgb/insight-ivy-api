# app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os  # <-- THIS IS MISSING - ADD THIS LINE
import secrets
from typing import Optional
from ..database import SessionLocal, User, Activity, Reflection, Goal

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer(auto_error=False)

# Now this will work
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", secrets.token_urlsafe(32))

# Simple token storage (in production, use Redis or database)
active_tokens = {}

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token with proper error handling"""
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        
        # Check if token exists
        if token not in active_tokens:
            print(f"Token not found in active_tokens: {token[:10]}...")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check expiration
        token_data = active_tokens[token]
        if isinstance(token_data, dict) and 'expires' in token_data:
            if token_data['expires'] < datetime.utcnow():
                del active_tokens[token]
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        elif token_data < datetime.utcnow():  # Handle old format
            del active_tokens[token]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return True
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any other errors and return proper 401
        print(f"Unexpected error in verify_admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/login")
async def admin_login(password: str = Body(..., embed=True)):
    """Login to admin dashboard"""
    try:
        if password == ADMIN_PASSWORD:
            # Store token with expiration (7 days)
            expires = datetime.utcnow() + timedelta(days=7)
            active_tokens[ADMIN_TOKEN] = {"expires": expires}
            
            return {
                "success": True, 
                "token": ADMIN_TOKEN,
                "expires": expires.isoformat()
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )