import random
from datetime import datetime

emotional_prompts = [
    "What emotion taught you something this week?",
    "What did today teach you about yourself?",
    "What is something you survived that you once thought you couldn't?",
    "When did you feel most at peace today?",
    "What triggered a strong emotion recently, and how did you handle it?",
    "What emotion are you avoiding right now?",
    "When did you feel proud of yourself this week?"
]

emotional_insights = {}

def get_emotional_prompt():
    """Return a random emotional awareness prompt"""
    return random.choice(emotional_prompts)

def save_emotional_insight(user_id: str, prompt: str, insight: str):
    """Save user's emotional insight"""
    if user_id not in emotional_insights:
        emotional_insights[user_id] = []
    
    entry = {
        "prompt": prompt,
        "insight": insight,
        "timestamp": datetime.now().isoformat()
    }
    emotional_insights[user_id].append(entry)
    
    # Analyze for growth patterns
    insights_count = len(emotional_insights[user_id])
    if insights_count >= 5:
        return f"💪 You've completed {insights_count} emotional reflections! Growing self-awareness!"
    
    return entry