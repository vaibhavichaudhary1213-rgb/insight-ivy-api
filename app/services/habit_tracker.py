from datetime import datetime, timedelta
from app.logger import logger

class HabitTracker:
    def __init__(self):
        self.habits = {}  # user_id -> {habit_name: habit_data}
        self.celebrations = {}  # user_id -> [celebrations]
    
    def add_habit(self, user_id: str, habit_name: str, habit_type: str = "build", target_days: int = 21):
        """Add a new habit to track"""
        if user_id not in self.habits:
            self.habits[user_id] = {}
        
        self.habits[user_id][habit_name] = {
            "name": habit_name,
            "type": habit_type,  # "build" or "quit"
            "target_days": target_days,
            "streak": 0,
            "longest_streak": 0,
            "total_completions": 0,
            "last_completed": None,
            "history": [],  # list of completion dates
            "created_at": datetime.now().isoformat()
        }
        
        return self.habits[user_id][habit_name]
    
    def track_habit(self, user_id: str, habit_name: str, completed: bool = True):
        """Track daily habit completion"""
        if user_id not in self.habits or habit_name not in self.habits[user_id]:
            return {"error": "Habit not found"}
        
        habit = self.habits[user_id][habit_name]
        today = datetime.now().date()
        
        if completed:
            # Check if already completed today
            last = habit.get("last_completed")
            if last and datetime.fromisoformat(last).date() == today:
                return {"message": "Already tracked today!", "streak": habit["streak"]}
            
            # Update streak
            habit["total_completions"] += 1
            habit["history"].append(datetime.now().isoformat())
            
            if last:
                last_date = datetime.fromisoformat(last).date()
                if (today - last_date).days == 1:
                    habit["streak"] += 1
                else:
                    # Streak broken
                    if habit["streak"] > habit["longest_streak"]:
                        habit["longest_streak"] = habit["streak"]
                    habit["streak"] = 1
            else:
                habit["streak"] = 1
            
            habit["last_completed"] = datetime.now().isoformat()
            
            # Check for milestones and celebrate
            celebrations = []
            
            if habit["streak"] in [3, 7, 14, 21, 30, 50, 100]:
                celebration = {
                    "type": "streak_milestone",
                    "message": f"🎉 {habit['streak']} day streak! You're on fire!",
                    "habit": habit_name,
                    "date": datetime.now().isoformat()
                }
                self._add_celebration(user_id, celebration)
                celebrations.append(celebration)
            
            if habit["total_completions"] in [10, 25, 50, 100]:
                celebration = {
                    "type": "total_milestone",
                    "message": f"🌟 {habit['total_completions']} total completions! Consistency is key!",
                    "habit": habit_name,
                    "date": datetime.now().isoformat()
                }
                self._add_celebration(user_id, celebration)
                celebrations.append(celebration)
            
            return {
                "habit": habit_name,
                "streak": habit["streak"],
                "total": habit["total_completions"],
                "celebrations": celebrations
            }
        
        return {"message": "Tracked", "habit": habit_name}
    
    def _add_celebration(self, user_id: str, celebration: dict):
        """Add a celebration for user"""
        if user_id not in self.celebrations:
            self.celebrations[user_id] = []
        self.celebrations[user_id].append(celebration)
    
    def get_habit_streak(self, user_id: str, habit_name: str):
        """Get current streak for a habit"""
        if user_id in self.habits and habit_name in self.habits[user_id]:
            habit = self.habits[user_id][habit_name]
            return {
                "habit": habit_name,
                "streak": habit["streak"],
                "longest": habit["longest_streak"],
                "total": habit["total_completions"]
            }
        return None
    
    def get_recent_celebrations(self, user_id: str, days: int = 7):
        """Get recent celebrations for a user"""
        if user_id not in self.celebrations:
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        for c in self.celebrations[user_id]:
            c_date = datetime.fromisoformat(c["date"])
            if c_date > cutoff:
                recent.append(c)
        
        return recent

habit_tracker = HabitTracker()