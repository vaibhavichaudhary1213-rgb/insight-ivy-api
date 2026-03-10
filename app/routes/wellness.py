from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.logger import logger
from app.services.wellness_tracker import wellness_tracker
from app.services.habit_tracker import habit_tracker
from app.services.happiness_tracker import happiness_tracker

router = APIRouter()

# Request Models
class SleepRequest(BaseModel):
    user_id: str
    hours: float
    quality: Optional[int] = None

class ExerciseRequest(BaseModel):
    user_id: str
    minutes: int
    intensity: str = "moderate"

class WaterRequest(BaseModel):
    user_id: str
    glasses: int

class MoodLogRequest(BaseModel):
    user_id: str
    mood: str
    intensity: int
    notes: str = ""

class HabitRequest(BaseModel):
    user_id: str
    habit_name: str
    habit_type: str = "build"
    target_days: int = 21

class HabitTrackRequest(BaseModel):
    user_id: str
    habit_name: str
    completed: bool = True

# -------------------------
# Wellness Tracking Endpoints
# -------------------------
@router.post("/track/sleep")
def track_sleep(request: SleepRequest):
    """Track sleep hours and quality"""
    logger.info(f"User {request.user_id} tracking sleep: {request.hours} hours")
    result = wellness_tracker.track_sleep(request.user_id, request.hours, request.quality)
    return result

@router.post("/track/exercise")
def track_exercise(request: ExerciseRequest):
    """Track exercise minutes"""
    logger.info(f"User {request.user_id} tracking exercise: {request.minutes} minutes")
    result = wellness_tracker.track_exercise(request.user_id, request.minutes, request.intensity)
    return result

@router.post("/track/water")
def track_water(request: WaterRequest):
    """Track water intake"""
    logger.info(f"User {request.user_id} tracking water: {request.glasses} glasses")
    result = wellness_tracker.track_water(request.user_id, request.glasses)
    return result

@router.get("/wellness/score/{user_id}")
def get_wellness_score(user_id: str, date: Optional[str] = None):
    """Get daily wellness score"""
    logger.info(f"Wellness score requested for user {user_id}")
    result = wellness_tracker.get_daily_wellness_score(user_id, date)
    return result

# -------------------------
# Habit Tracking Endpoints
# -------------------------
@router.post("/habits/add")
def add_habit(request: HabitRequest):
    """Add a new habit to track"""
    logger.info(f"User {request.user_id} adding habit: {request.habit_name}")
    result = habit_tracker.add_habit(
        request.user_id, 
        request.habit_name, 
        request.habit_type,
        request.target_days
    )
    return result

@router.post("/habits/track")
def track_habit(request: HabitTrackRequest):
    """Track daily habit completion"""
    logger.info(f"User {request.user_id} tracking habit: {request.habit_name}")
    result = habit_tracker.track_habit(request.user_id, request.habit_name, request.completed)
    return result

@router.get("/habits/streak/{user_id}/{habit_name}")
def get_habit_streak(user_id: str, habit_name: str):
    """Get current streak for a habit"""
    result = habit_tracker.get_habit_streak(user_id, habit_name)
    if not result:
        raise HTTPException(status_code=404, detail="Habit not found")
    return result

@router.get("/habits/celebrations/{user_id}")
def get_recent_celebrations(user_id: str, days: int = 7):
    """Get recent habit celebrations"""
    result = habit_tracker.get_recent_celebrations(user_id, days)
    return {"celebrations": result}

# -------------------------
# Happiness Tracking Endpoints
# -------------------------
@router.post("/happiness/log")
def log_mood(request: MoodLogRequest):
    """Log daily mood and get happiness score"""
    logger.info(f"User {request.user_id} logging mood: {request.mood}")
    result = happiness_tracker.log_mood(
        request.user_id, 
        request.mood, 
        request.intensity,
        request.notes
    )
    return result

@router.get("/happiness/weekly/{user_id}")
def get_weekly_mood_graph(user_id: str):
    """Get data for weekly mood graph"""
    logger.info(f"Weekly mood graph requested for user {user_id}")
    data = happiness_tracker.get_weekly_mood_graph(user_id)
    average = happiness_tracker.calculate_weekly_average(user_id)
    
    return {
        "graph_data": data,
        "weekly_average": average
    }

@router.get("/happiness/trends/{user_id}")
def get_mood_trends(user_id: str):
    """Get mood trend analysis"""
    logger.info(f"Mood trends requested for user {user_id}")
    result = happiness_tracker.get_mood_trends(user_id)
    return result