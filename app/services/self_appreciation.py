import random
from datetime import datetime

appreciation_prompts = [
    "What is one quality you like in yourself?",
    "What is one effort you're proud of?",
    "When did you show strength recently?",
    "What's something your younger self would admire about you?",
    "What's a challenge you handled gracefully?",
    "When did you put someone else's needs before yours?",
    "What's a skill you've improved recently?",
    "What's something unique about your perspective?"
]

self_appreciations = {}

def get_appreciation_prompt():
    """Return a self-appreciation prompt"""
    return random.choice(appreciation_prompts)

def save_self_appreciation(user_id: str, prompt: str, appreciation: str):
    """Save self-appreciation entry"""
    if user_id not in self_appreciations:
        self_appreciations[user_id] = []
    
    entry = {
        "prompt": prompt,
        "appreciation": appreciation,
        "timestamp": datetime.now().isoformat()
    }
    self_appreciations[user_id].append(entry)
    
    # Build self-appreciation collection
    collection = self_appreciations[user_id]
    if len(collection) == 1:
        return "🎯 First appreciation logged! This is the start of something beautiful."
    elif len(collection) == 5:
        return "🌟 5 appreciations! You're building a powerful self-love collection."
    elif len(collection) == 10:
        return "💫 DOUBLE DIGITS! You've appreciated yourself 10 times. That's amazing!"
    
    return entry