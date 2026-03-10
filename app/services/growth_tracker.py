from datetime import datetime, timedelta
from app.logger import logger

user_growth_data = {}

def init_user_growth(user_id: str):
    """Initialize growth tracking for a user"""
    if user_id not in user_growth_data:
        user_growth_data[user_id] = {
            "long_term_goal": None,
            "academic_pressure": [],
            "biggest_fear": None,
            "habits_to_build": [],
            "habits_to_stop": [],
            "weekly_wins": [],
            "milestones": []
        }

def set_long_term_goal(user_id: str, goal: str):
    """Set user's long-term goal"""
    init_user_growth(user_id)
    user_growth_data[user_id]["long_term_goal"] = {
        "goal": goal,
        "set_date": datetime.now().isoformat(),
        "progress": []
    }
    logger.info(f"Long-term goal set for user {user_id}")

def track_academic_pressure(user_id: str, level: int):
    """Track academic pressure level (1-5)"""
    init_user_growth(user_id)
    
    pressure_entry = {
        "level": min(max(level, 1), 5),
        "timestamp": datetime.now().isoformat()
    }
    
    user_growth_data[user_id]["academic_pressure"].append(pressure_entry)
    
    # Calculate trend
    recent = user_growth_data[user_id]["academic_pressure"][-7:]  # Last 7 entries
    if len(recent) >= 3:
        avg_pressure = sum(p["level"] for p in recent) / len(recent)
        if avg_pressure > 4:
            return "⚠️ Your stress levels have been consistently high. Consider taking a break!"
        elif avg_pressure < 2:
            return "✨ You're managing stress well! Keep up the good balance."
    
    return pressure_entry

def set_biggest_fear(user_id: str, fear: str):
    """Set user's biggest fear"""
    init_user_growth(user_id)
    user_growth_data[user_id]["biggest_fear"] = {
        "fear": fear,
        "set_date": datetime.now().isoformat()
    }

def add_habit_to_build(user_id: str, habit: str):
    """Add a habit user wants to build"""
    init_user_growth(user_id)
    habit_entry = {
        "habit": habit,
        "started": datetime.now().isoformat(),
        "streak": 0,
        "completed_dates": []
    }
    user_growth_data[user_id]["habits_to_build"].append(habit_entry)
    return habit_entry

def add_habit_to_stop(user_id: str, habit: str):
    """Add a habit user wants to stop"""
    init_user_growth(user_id)
    habit_entry = {
        "habit": habit,
        "started": datetime.now().isoformat(),
        "days_without": 0,
        "struggle_dates": []
    }
    user_growth_data[user_id]["habits_to_stop"].append(habit_entry)
    return habit_entry

def track_habit_progress(user_id: str, habit_name: str, completed: bool):
    """Track daily habit completion"""
    init_user_growth(user_id)
    
    # Check habits to build
    for habit in user_growth_data[user_id]["habits_to_build"]:
        if habit["habit"].lower() == habit_name.lower():
            if completed:
                today = datetime.now().date().isoformat()
                if today not in habit["completed_dates"]:
                    habit["completed_dates"].append(today)
                    habit["streak"] += 1
                    
                    # Celebrate milestones
                    if habit["streak"] in [3, 7, 14, 21, 30]:
                        return f"🎉 Amazing! {habit['streak']} day streak! You're building momentum!"
            return {"streak": habit["streak"], "total_days": len(habit["completed_dates"])}
    
    return None

def add_weekly_win(user_id: str, win: str):
    """Add a small academic win"""
    init_user_growth(user_id)
    win_entry = {
        "win": win,
        "week": datetime.now().isocalendar()[1],
        "timestamp": datetime.now().isoformat()
    }
    user_growth_data[user_id]["weekly_wins"].append(win_entry)
    
    # Count wins this week
    current_week = datetime.now().isocalendar()[1]
    weekly_wins = [w for w in user_growth_data[user_id]["weekly_wins"] if w["week"] == current_week]
    
    if len(weekly_wins) >= 3:
        return f"🌟 You've had {len(weekly_wins)} wins this week! You're on fire!"
    
    return win_entry