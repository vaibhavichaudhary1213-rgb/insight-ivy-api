from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.logger import logger
from app.services.joy_triggers import *
from app.services.growth_tracker import *
from app.services.student_prompts import *
from app.services.emotional_awareness import *
from app.services.micro_gratitude import *
from app.services.self_appreciation import *
from app.services.kindness_extended import *

router = APIRouter()

# Request Models
class JoyTriggerRequest(BaseModel):
    user_id: str
    question: str
    answer: str

class GrowthGoalRequest(BaseModel):
    user_id: str
    goal: str

class AcademicPressureRequest(BaseModel):
    user_id: str
    level: int

class FearRequest(BaseModel):
    user_id: str
    fear: str

class HabitRequest(BaseModel):
    user_id: str
    habit: str

class HabitProgressRequest(BaseModel):
    user_id: str
    habit_name: str
    completed: bool

class WinRequest(BaseModel):
    user_id: str
    win: str

class PromptResponseRequest(BaseModel):
    user_id: str
    prompt: str
    response: str

class KindnessCompleteRequest(BaseModel):
    user_id: str
    challenge: str

# -------------------------
# Joy Triggers Endpoints
# -------------------------
@router.get("/joy/question")
def get_joy_question():
    """Get a random joy trigger question"""
    question = get_random_joy_question()
    return {"question": question}

@router.post("/joy/answer")
def save_joy_answer(request: JoyTriggerRequest):
    """Save user's answer to joy trigger"""
    result = save_joy_trigger(request.user_id, request.question, request.answer)
    return result

@router.get("/joy/triggers/{user_id}")
def get_user_joy_triggers_endpoint(user_id: str):
    """Get all joy triggers for a user"""
    triggers = get_user_joy_triggers(user_id)
    return {"triggers": triggers}

# -------------------------
# Growth & Motivation Endpoints
# -------------------------
@router.post("/growth/goal")
def set_long_term_goal_endpoint(request: GrowthGoalRequest):
    """Set long-term goal"""
    result = set_long_term_goal(request.user_id, request.goal)
    return {"message": "Goal set successfully"}

@router.post("/growth/pressure")
def track_academic_pressure_endpoint(request: AcademicPressureRequest):
    """Track academic pressure"""
    result = track_academic_pressure(request.user_id, request.level)
    return result

@router.post("/growth/fear")
def set_biggest_fear_endpoint(request: FearRequest):
    """Set biggest fear"""
    result = set_biggest_fear(request.user_id, request.fear)
    return {"message": "Fear recorded"}

@router.post("/growth/habit/build")
def add_habit_to_build_endpoint(request: HabitRequest):
    """Add habit to build"""
    result = add_habit_to_build(request.user_id, request.habit)
    return result

@router.post("/growth/habit/stop")
def add_habit_to_stop_endpoint(request: HabitRequest):
    """Add habit to stop"""
    result = add_habit_to_stop(request.user_id, request.habit)
    return result

@router.post("/growth/habit/progress")
def track_habit_progress_endpoint(request: HabitProgressRequest):
    """Track habit progress"""
    result = track_habit_progress(request.user_id, request.habit_name, request.completed)
    return result

@router.post("/growth/win")
def add_weekly_win_endpoint(request: WinRequest):
    """Add weekly win"""
    result = add_weekly_win(request.user_id, request.win)
    return result

# -------------------------
# Student Prompts Endpoints
# -------------------------
@router.get("/student/prompt")
def get_student_prompt_endpoint():
    """Get a student-focused prompt"""
    prompt = get_student_prompt()
    return {"prompt": prompt}

@router.post("/student/response")
def save_student_response_endpoint(request: PromptResponseRequest):
    """Save response to student prompt"""
    result = save_student_response(request.user_id, request.prompt, request.response)
    return result

# -------------------------
# Emotional Awareness Endpoints
# -------------------------
@router.get("/emotional/prompt")
def get_emotional_prompt_endpoint():
    """Get an emotional awareness prompt"""
    prompt = get_emotional_prompt()
    return {"prompt": prompt}

@router.post("/emotional/insight")
def save_emotional_insight_endpoint(request: PromptResponseRequest):
    """Save emotional insight"""
    result = save_emotional_insight(request.user_id, request.prompt, request.insight)
    return result

# -------------------------
# Micro-Gratitude Endpoints
# -------------------------
@router.get("/gratitude/micro")
def get_micro_gratitude_endpoint():
    """Get a micro-gratitude prompt"""
    prompt = get_micro_gratitude_prompt()
    return {"prompt": prompt}

@router.post("/gratitude/micro")
def save_micro_gratitude_endpoint(request: PromptResponseRequest):
    """Save micro-gratitude response"""
    result = save_micro_gratitude(request.user_id, request.prompt, request.response)
    return result

@router.get("/gratitude/recent/{user_id}")
def get_recent_gratitudes_endpoint(user_id: str, days: int = 7):
    """Get recent gratitude entries"""
    recent = get_recent_gratitudes(user_id, days)
    return {"recent_gratitudes": recent}

# -------------------------
# Self-Appreciation Endpoints
# -------------------------
@router.get("/appreciation/prompt")
def get_appreciation_prompt_endpoint():
    """Get a self-appreciation prompt"""
    prompt = get_appreciation_prompt()
    return {"prompt": prompt}

@router.post("/appreciation/save")
def save_self_appreciation_endpoint(request: PromptResponseRequest):
    """Save self-appreciation"""
    result = save_self_appreciation(request.user_id, request.prompt, request.appreciation)
    return result

# -------------------------
# Extended Kindness Endpoints
# -------------------------
@router.get("/kindness/challenge")
def get_kindness_challenge_endpoint(category: str = "all"):
    """Get a kindness challenge"""
    challenge = get_kindness_challenge(category)
    return {"challenge": challenge}

@router.post("/kindness/complete")
def complete_kindness_challenge_endpoint(request: KindnessCompleteRequest):
    """Mark kindness challenge as complete"""
    result = complete_kindness_challenge(request.user_id, request.challenge)
    return result

@router.get("/kindness/stats/{user_id}")
def get_kindness_stats_endpoint(user_id: str):
    """Get kindness challenge statistics"""
    stats = get_kindness_stats(user_id)
    return stats