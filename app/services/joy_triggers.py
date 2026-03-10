import random
from datetime import datetime
from app.logger import logger

# User-specific joy triggers storage
user_joy_triggers = {}

joy_questions = [
    "What makes you feel calm?",
    "What instantly makes you smile?",
    "Who is your biggest support person?",
    "One childhood memory you love?",
    "One dream destination?"
]

def get_random_joy_question():
    """Return a random joy trigger question"""
    return random.choice(joy_questions)

def save_joy_trigger(user_id: str, question: str, answer: str):
    """Save user's answer to a joy trigger question"""
    if user_id not in user_joy_triggers:
        user_joy_triggers[user_id] = []
    
    trigger_entry = {
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    }
    
    user_joy_triggers[user_id].append(trigger_entry)
    logger.info(f"Joy trigger saved for user {user_id}")
    return trigger_entry

def get_user_joy_triggers(user_id: str):
    """Get all joy triggers for a user"""
    return user_joy_triggers.get(user_id, [])