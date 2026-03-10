from datetime import datetime, timedelta
from app.logger import logger

class WellnessTracker:
    def __init__(self):
        self.sleep_data = {}  # user_id -> list of sleep entries
        self.exercise_data = {}  # user_id -> list of exercise entries
        self.water_data = {}  # user_id -> list of water entries
        self.wellness_scores = {}  # user_id -> daily scores
    
    def track_sleep(self, user_id: str, hours: float, quality: int = None):
        """Track sleep hours and quality"""
        if user_id not in self.sleep_data:
            self.sleep_data[user_id] = []
        
        entry = {
            "hours": hours,
            "quality": quality,  # 1-5 scale
            "date": datetime.now().date().isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.sleep_data[user_id].append(entry)
        
        # Provide insights
        insights = []
        if hours < 6:
            insights.append("😴 You got less than 6 hours of sleep. Try to prioritize rest tonight.")
        elif hours > 9:
            insights.append("😊 That's plenty of rest! How do you feel?")
        elif hours >= 7 and hours <= 8:
            insights.append("✨ Perfect sleep duration! That's the sweet spot.")
        
        # Check weekly average
        weekly = self.get_weekly_sleep_avg(user_id)
        if weekly:
            if weekly < 6.5:
                insights.append(f"📊 Your weekly average is {weekly:.1f} hours. Consider adjusting your sleep schedule.")
            elif weekly >= 7:
                insights.append(f"📊 Great weekly average of {weekly:.1f} hours! Keep it up!")
        
        return {
            "entry": entry,
            "insights": insights
        }
    
    def track_exercise(self, user_id: str, minutes: int, intensity: str = "moderate"):
        """Track exercise minutes"""
        if user_id not in self.exercise_data:
            self.exercise_data[user_id] = []
        
        entry = {
            "minutes": minutes,
            "intensity": intensity,  # light, moderate, vigorous
            "date": datetime.now().date().isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.exercise_data[user_id].append(entry)
        
        # Calculate weekly total
        weekly_total = self.get_weekly_exercise_total(user_id)
        
        insights = []
        if weekly_total >= 150:
            insights.append("🎯 You've hit the recommended 150 minutes of weekly exercise! Amazing!")
        elif weekly_total >= 75:
            insights.append(f"💪 {weekly_total} minutes this week. Halfway to the weekly goal!")
        
        return {
            "entry": entry,
            "weekly_total": weekly_total,
            "insights": insights
        }
    
    def track_water(self, user_id: str, glasses: int):
        """Track water intake"""
        if user_id not in self.water_data:
            self.water_data[user_id] = []
        
        today = datetime.now().date().isoformat()
        
        # Check if we already have an entry for today
        for entry in self.water_data[user_id]:
            if entry["date"] == today:
                entry["glasses"] += glasses
                entry["timestamp"] = datetime.now().isoformat()
                return self._get_water_feedback(entry["glasses"])
        
        # New entry for today
        entry = {
            "glasses": glasses,
            "date": today,
            "timestamp": datetime.now().isoformat()
        }
        self.water_data[user_id].append(entry)
        
        return self._get_water_feedback(glasses)
    
    def _get_water_feedback(self, glasses):
        """Get feedback based on water intake"""
        feedback = {
            "glasses": glasses,
            "message": "",
            "goal": 8
        }
        
        if glasses >= 8:
            feedback["message"] = "💧 Excellent hydration! You've met your daily goal!"
        elif glasses >= 6:
            feedback["message"] = f"💧 Good progress! {glasses}/8 glasses. Keep drinking!"
        elif glasses >= 4:
            feedback["message"] = f"💧 {glasses}/8 glasses. Try to drink more throughout the day."
        else:
            feedback["message"] = f"💧 Only {glasses} glass{'es' if glasses > 1 else ''} today. Time to hydrate!"
        
        return feedback
    
    def get_weekly_sleep_avg(self, user_id: str):
        """Calculate average sleep for the last 7 days"""
        if user_id not in self.sleep_data:
            return None
        
        cutoff = datetime.now() - timedelta(days=7)
        recent = []
        for entry in self.sleep_data[user_id]:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            if entry_date > cutoff:
                recent.append(entry["hours"])
        
        if recent:
            return sum(recent) / len(recent)
        return None
    
    def get_weekly_exercise_total(self, user_id: str):
        """Calculate total exercise minutes for the last 7 days"""
        if user_id not in self.exercise_data:
            return 0
        
        cutoff = datetime.now() - timedelta(days=7)
        total = 0
        for entry in self.exercise_data[user_id]:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            if entry_date > cutoff:
                total += entry["minutes"]
        
        return total
    
    def get_daily_wellness_score(self, user_id: str, date=None):
        """Calculate a daily wellness score (0-100)"""
        if date is None:
            date = datetime.now().date().isoformat()
        
        score = 0
        factors = []
        
        # Check sleep
        if user_id in self.sleep_data:
            for entry in reversed(self.sleep_data[user_id]):
                if entry["date"] == date:
                    if entry["hours"] >= 7:
                        score += 30
                        factors.append("good_sleep")
                    elif entry["hours"] >= 6:
                        score += 15
                        factors.append("ok_sleep")
                    break
        
        # Check exercise
        if user_id in self.exercise_data:
            for entry in reversed(self.exercise_data[user_id]):
                if entry["date"] == date:
                    if entry["minutes"] >= 30:
                        score += 30
                        factors.append("good_exercise")
                    elif entry["minutes"] >= 15:
                        score += 15
                        factors.append("ok_exercise")
                    break
        
        # Check water
        if user_id in self.water_data:
            for entry in reversed(self.water_data[user_id]):
                if entry["date"] == date:
                    if entry["glasses"] >= 8:
                        score += 40
                        factors.append("good_water")
                    elif entry["glasses"] >= 5:
                        score += 20
                        factors.append("ok_water")
                    break
        
        return {
            "date": date,
            "score": score,
            "factors": factors,
            "interpretation": self._interpret_score(score)
        }
    
    def _interpret_score(self, score):
        """Interpret wellness score"""
        if score >= 80:
            return "🌟 Excellent self-care day! You're thriving!"
        elif score >= 60:
            return "💪 Good day! Small improvements make a big difference."
        elif score >= 40:
            return "🌱 You're trying. Tomorrow is a fresh start."
        else:
            return "🌸 Be kind to yourself. Every small step counts."

wellness_tracker = WellnessTracker()