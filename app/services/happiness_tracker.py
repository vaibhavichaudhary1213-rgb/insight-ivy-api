from datetime import datetime, timedelta
import statistics
from collections import defaultdict
from app.logger import logger

class HappinessTracker:
    def __init__(self):
        self.mood_entries = {}  # user_id -> list of mood entries
        self.happiness_scores = {}  # user_id -> daily scores
    
    def log_mood(self, user_id: str, mood: str, intensity: int, notes: str = ""):
        """Log a daily mood entry"""
        if user_id not in self.mood_entries:
            self.mood_entries[user_id] = []
        
        today = datetime.now().date().isoformat()
        
        # Check if already logged today
        for entry in reversed(self.mood_entries[user_id]):
            if entry["date"] == today:
                # Update today's entry
                entry["mood"] = mood
                entry["intensity"] = intensity
                entry["notes"] = notes
                entry["updated_at"] = datetime.now().isoformat()
                return self._calculate_happiness_score(user_id, entry)
        
        # New entry
        entry = {
            "mood": mood,
            "intensity": intensity,
            "notes": notes,
            "date": today,
            "timestamp": datetime.now().isoformat()
        }
        
        self.mood_entries[user_id].append(entry)
        
        # Calculate happiness score for the day
        return self._calculate_happiness_score(user_id, entry)
    
    def _calculate_happiness_score(self, user_id: str, entry):
        """Calculate happiness score for an entry"""
        # Base score from intensity (1-5)
        base_score = entry["intensity"] * 20  # 20-100
        
        # Mood multiplier
        positive_moods = ["happy", "excited", "grateful", "calm", "hopeful", "proud", "confident", "motivated"]
        negative_moods = ["sad", "angry", "anxious", "stressed", "lonely", "hurt", "frustrated"]
        
        if entry["mood"].lower() in positive_moods:
            multiplier = 1.0
        elif entry["mood"].lower() in negative_moods:
            multiplier = 0.6
        else:
            multiplier = 0.8
        
        final_score = int(base_score * multiplier)
        
        # Store the score
        if user_id not in self.happiness_scores:
            self.happiness_scores[user_id] = []
        
        # Update or add score for today
        today = entry["date"]
        for score_entry in self.happiness_scores[user_id]:
            if score_entry["date"] == today:
                score_entry["score"] = final_score
                score_entry["mood"] = entry["mood"]
                break
        else:
            self.happiness_scores[user_id].append({
                "date": today,
                "score": final_score,
                "mood": entry["mood"]
            })
        
        return {
            "date": today,
            "mood": entry["mood"],
            "intensity": entry["intensity"],
            "happiness_score": final_score
        }
    
    def get_weekly_mood_graph(self, user_id: str):
        """Generate data for weekly mood graph"""
        if user_id not in self.mood_entries:
            return []
        
        cutoff = datetime.now() - timedelta(days=7)
        weekly_data = []
        
        # Get last 7 days of data
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            date_str = date.isoformat()
            
            # Find entry for this date
            entry = None
            for e in reversed(self.mood_entries[user_id]):
                if e["date"] == date_str:
                    entry = e
                    break
            
            day_data = {
                "date": date.strftime("%a"),  # Mon, Tue, etc.
                "full_date": date_str,
                "mood": entry["mood"] if entry else None,
                "intensity": entry["intensity"] if entry else None,
                "happiness_score": None
            }
            
            # Get happiness score
            if user_id in self.happiness_scores:
                for score in self.happiness_scores[user_id]:
                    if score["date"] == date_str:
                        day_data["happiness_score"] = score["score"]
                        break
            
            weekly_data.append(day_data)
        
        return weekly_data
    
    def calculate_weekly_average(self, user_id: str):
        """Calculate average happiness score for the week"""
        if user_id not in self.happiness_scores:
            return None
        
        cutoff = datetime.now() - timedelta(days=7)
        weekly_scores = []
        
        for entry in self.happiness_scores[user_id]:
            entry_date = datetime.fromisoformat(entry["date"])
            if entry_date > cutoff:
                weekly_scores.append(entry["score"])
        
        if weekly_scores:
            avg_score = sum(weekly_scores) / len(weekly_scores)
            return {
                "average": round(avg_score, 1),
                "min": min(weekly_scores),
                "max": max(weekly_scores),
                "days_tracked": len(weekly_scores)
            }
        
        return None
    
    def get_mood_trends(self, user_id: str):
        """Analyze mood trends over time"""
        if user_id not in self.mood_entries or len(self.mood_entries[user_id]) < 3:
            return {"message": "Not enough data for trend analysis"}
        
        entries = self.mood_entries[user_id]
        recent = entries[-7:]  # Last 7 entries
        
        # Count mood frequencies
        mood_counts = defaultdict(int)
        for entry in recent:
            mood_counts[entry["mood"]] += 1
        
        # Find most common mood
        most_common = max(mood_counts, key=mood_counts.get) if mood_counts else None
        
        # Calculate trend (are scores improving?)
        if len(recent) >= 3:
            first_three = recent[:3]
            last_three = recent[-3:]
            
            first_avg = sum(e["intensity"] for e in first_three) / 3
            last_avg = sum(e["intensity"] for e in last_three) / 3
            
            if last_avg > first_avg + 0.5:
                trend = "improving"
            elif last_avg < first_avg - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Generate insights
        insights = []
        if most_common:
            if most_common in ["sad", "anxious", "stressed"]:
                insights.append(f"📊 {most_common.capitalize()} has been frequent lately. Be gentle with yourself.")
            elif most_common in ["happy", "calm", "excited"]:
                insights.append(f"✨ You've been feeling {most_common} often! That's wonderful.")
        
        if trend == "improving":
            insights.append("📈 Your mood intensity has been improving! Keep doing what you're doing.")
        elif trend == "declining":
            insights.append("📉 Your mood has dipped recently. Remember it's okay to ask for help.")
        
        return {
            "mood_distribution": dict(mood_counts),
            "most_common_mood": most_common,
            "trend": trend,
            "insights": insights,
            "total_entries": len(entries),
            "recent_entries": len(recent)
        }

happiness_tracker = HappinessTracker()