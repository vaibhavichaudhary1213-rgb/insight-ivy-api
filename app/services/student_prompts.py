import random
from datetime import datetime

student_prompts = [
    "What is one small academic win this week?",
    "Who helped you understand something recently?",
    "What subject do you secretly enjoy?",
    "What is one thing you handled better than last year?",
    "What's a concept that finally 'clicked' for you?",
    "Which classmate inspired you recently?",
    "What study method worked well for you this week?",
    "What's something you learned outside of class?"
]

def get_student_prompt():
    """Return a random student-focused prompt"""
    return random.choice(student_prompts)

# Store responses
student_responses = {}

def save_student_response(user_id: str, prompt: str, response: str):
    """Save student's response to a prompt"""
    if user_id not in student_responses:
        student_responses[user_id] = []
    
    entry = {
        "prompt": prompt,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }
    student_responses[user_id].append(entry)
    return entry