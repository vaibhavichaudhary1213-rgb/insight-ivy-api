emotion_memory = {}

def store_emotion(user_id: str, emotion: str):
    """Store emotion (original simple version)"""
    if user_id not in emotion_memory:
        emotion_memory[user_id] = []
    emotion_memory[user_id].append(emotion)

def get_emotion_history(user_id: str):
    """Get emotion history"""
    return emotion_memory.get(user_id, [])