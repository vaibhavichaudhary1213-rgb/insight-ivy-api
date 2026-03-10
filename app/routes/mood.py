from fastapi import APIRouter
from pydantic import BaseModel
from app.logger import logger

from app.services.emotion_classifier import classify_emotion
from app.services.response_engine import generate_response
from app.services.safety_engine import (
    detect_risk, 
    crisis_response, 
    detect_medium_risk, 
    medium_risk_response
)
from app.services.gratitude_engine import generate_gratitude
from app.services.kindness_engine import generate_kindness
from app.services.memory_engine import store_emotion, get_emotion_history
from app.services.analytics_engine import track_message, track_high_risk

router = APIRouter()

# -------------------------
# Request Model
# -------------------------
class MoodRequest(BaseModel):
    user_id: str
    text: str
    intensity: int


# -------------------------
# Mood Analysis API
# -------------------------
@router.post("/analyze")
def analyze_mood(request: MoodRequest):

    logger.info(f"User {request.user_id} message: {request.text}")

    # --------------------
    # 1️⃣ High-risk check
    # --------------------
    risk_level = detect_risk(request.text)

    if risk_level == "high":

        logger.warning(f"HIGH RISK detected for user {request.user_id}")

        track_high_risk(request.user_id)

        return {
            "sentiment": "Critical",
            "primary_emotion": "High Risk",
            "intensity": 5,
            "context_tags": ["Mental health risk"],
            "chatbot_response": crisis_response(),
            "emotion_history": [],
            "pattern_alert": None,
            "gratitude_prompt": None,
            "kindness_challenge": None
        }
    
    # --------------------
    # Medium Risk Check
    # --------------------
    if detect_medium_risk(request.text):

        logger.warning(f"MEDIUM RISK detected for user {request.user_id}")

        return {
            "sentiment": "Negative",
            "primary_emotion": "Distress",
            "intensity": 4,
            "context_tags": ["Emotional distress"],
            "chatbot_response": medium_risk_response(),
            "emotion_history": [],
            "pattern_alert": None,
            "gratitude_prompt": None,
            "kindness_challenge": None
        }

    # --------------------
    # 2️⃣ Emotion classification
    # --------------------
    emotion_result = classify_emotion(request.text, request.intensity)

    sentiment = emotion_result["sentiment"]
    primary_emotion = emotion_result["primary_emotion"]
    context_tags = emotion_result["context_tags"]
    detected_intensity = emotion_result["intensity"]

    logger.info(
        f"Emotion detected: {primary_emotion} | "
        f"Sentiment: {sentiment} | "
        f"Intensity: {detected_intensity}"
    )

    logger.info(f"Context tags: {context_tags}")

    # --------------------
    # 3️⃣ Store emotion in memory
    # --------------------
    # Store with full context
    store_emotion(request.user_id, primary_emotion)

    history = get_emotion_history(request.user_id)

    # --------------------
    # 4️⃣ Generate chatbot response
    # --------------------
    chatbot_reply = generate_response(
        primary_emotion,
        detected_intensity,
        context_tags
    )

    # --------------------
    # 5️⃣ Detect emotion patterns
    # --------------------
    pattern_alert = None

    # Look at the last 5 recorded emotions
    recent = [entry["emotion"].lower() for entry in history[-5:] if "emotion" in entry]

    # Detect repeated sadness
    if recent.count("sad") >= 3:
        pattern_alert = (
            "You seem to have been feeling sad quite often recently. "
            "Would you like to talk about what has been going on?"
        )

    # Detect repeated stress/anxiety
    elif recent.count("anxious") >= 3 or recent.count("stressed") >= 3:
        pattern_alert = "It seems like stress has been showing up frequently lately. Would you like to share what has been causing the most pressure?" 

    if pattern_alert:
        logger.info(f"Emotion pattern detected for user {request.user_id}")


    # --------------------
    # 6️⃣ Track analytics
    # --------------------
    track_message(request.user_id, primary_emotion)

    logger.info(f"Analytics updated for user {request.user_id} emotion {primary_emotion}")

    # --------------------
    # 7️⃣ Return enriched response
    # --------------------
    return {
        "sentiment": sentiment,
        "primary_emotion": primary_emotion,
        "intensity": detected_intensity,
        "context_tags": context_tags,
        "chatbot_response": chatbot_reply,
        "emotion_history": history,
        "pattern_alert": pattern_alert,
        "gratitude_prompt": generate_gratitude(),
        "kindness_challenge": generate_kindness()
    }

