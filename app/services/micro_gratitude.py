import random
from datetime import datetime, timedelta 

micro_gratitude_prompts = [
    "One good smell you noticed today?",
    "One moment of silence you appreciated?",
    "One random smile you saw?",
    "One small comfort today?",
    "One warm drink you enjoyed?",
    "One comfortable texture you touched?",
    "One beautiful thing you saw?",
    "One sound that made you smile?",
    "One thing that made you laugh today?",
    "One thing your body did well today?"
]

# Enhanced gratitude engine
def get_micro_gratitude_prompt():
    """Return a micro-gratitude prompt"""
    return random.choice(micro_gratitude_prompts)

# Store gratitude entries
gratitude_journal = {}

def save_micro_gratitude(user_id: str, prompt: str, answer: str):
    """Save micro-gratitude entry"""
    if user_id not in gratitude_journal:
        gratitude_journal[user_id] = []
    
    entry = {
        "prompt": prompt,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    }
    gratitude_journal[user_id].append(entry)
    
    # Provide positive reinforcement
    entries_count = len(gratitude_journal[user_id])
    if entries_count % 5 == 0:
        return f"🌈 You've recorded {entries_count} moments of gratitude! Your positivity journal is growing!"
    
    return entry

def get_recent_gratitudes(user_id: str, days: int = 7):
    """Get recent gratitude entries"""
    entries = gratitude_journal.get(user_id, [])
    cutoff = datetime.now() - timedelta(days=days)
    
    recent = []
    for entry in entries:
        entry_date = datetime.fromisoformat(entry["timestamp"])
        if entry_date > cutoff:
            recent.append(entry)
    
    return recent