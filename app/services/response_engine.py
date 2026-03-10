from app.logger import logger

def generate_response(emotion, intensity=3, context_tags=None, history=None):

    emotion = emotion.strip().lower()
    
    if context_tags is None:
        context_tags = []

    if history is None:
        history = []

    # -----------------------------
    # Stress / Anxiety
    # -----------------------------
    if emotion in ["anxious", "overwhelmed", "stressed", "confused"]:

        response = (
            "It sounds like things feel pretty heavy right now. "
            "That reaction is completely understandable."
        )

        if context_tags and "Academic stress" in context_tags:
            response += (
                " Academic pressure can build up quickly, especially during exams or deadlines."
            )

        if intensity >= 4:
            response += (
                " Let's pause for a moment. "
                "Try taking three slow breaths and relaxing your shoulders. "
                "What part of this situation feels the most overwhelming right now?"
            )
        else:
            response += (
                " Sometimes even a small reset helps. "
                "Would taking a short walk or stretching for a minute help you feel a bit lighter?"
            )

    # -----------------------------
    # Sadness
    # -----------------------------
    elif emotion in ["sad", "lonely", "hopeless"]:

        response = (
            "I'm really glad you shared that with me. "
            "Feeling this way doesn't mean there's something wrong with you."
        )

        if intensity >= 4:
            response += (
                " When emotions feel strong, talking about them can sometimes ease the pressure. "
                "What do you think has been weighing on you the most lately?"
            )
        else:
            response += (
                " Sometimes writing down your thoughts or reaching out to someone you trust "
                "can help a little. "
                "Has anything small brought you comfort recently?"
            )

    # -----------------------------
    # Positive emotions
    # -----------------------------
    elif emotion in ["happy", "excited", "proud"]:

        response = (
            "That's really wonderful to hear 🌸 "
            "Moments like that can be meaningful."
        )

        response += (
            " What made this moment feel special to you?"
        )

    # -----------------------------
    # Anger
    # -----------------------------
    elif emotion == "angry":

        response = (
            "That sounds frustrating. "
            "Anyone might feel upset in a situation like that."
        )

        response += (
            " Sometimes stepping away briefly or taking a few slow breaths "
            "can help the mind reset. "
            "What happened that triggered this feeling?"
        )

    # -----------------------------
    # Mixed emotions
    # -----------------------------
    elif emotion == "mixed":

        response = (
            "It sounds like you're experiencing several emotions at once. "
            "That can happen when situations are complex."
        )

        response += (
            " Would you like to share what parts of the situation feel positive "
            "and which parts feel difficult?"
        )

    # -----------------------------
    # Neutral / Unknown
    # -----------------------------
    else:

        response = (
            "Thank you for sharing how you're feeling. "
            "Reflecting on emotions can sometimes help us understand them better."
        )

        response += (
            " How has this been affecting your day?"
        )

    # Context-aware additions
    if context_tags:

        if "Academic stress" in context_tags:
            response += (
                " Exams and academic pressure can feel really overwhelming sometimes."
            )

        if "Career uncertainty" in context_tags:
            response += (
                " Thinking about the future and career choices can bring a lot of pressure."
            )

        if "Social relationships" in context_tags:
            response += (
                " Relationships and friendships can sometimes bring complex emotions."
            )
    
    # Pattern detection
    recent = history[-5:]

    if recent.count("sad") >= 3:
        response += (
            " I also notice you've been feeling sad several times recently. "
            "If you'd like, we can talk about what has been making things difficult."
        )
    
    logger.info(f"Emotion: {emotion} | Context: {context_tags}")

    return response

