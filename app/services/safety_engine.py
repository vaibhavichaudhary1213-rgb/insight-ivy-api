from app.logger import logger


def detect_risk(text: str):
    """
    Detect severe crisis language.
    Returns: high / medium / low
    """

    text = text.lower()

    crisis_keywords = [
        "suicide",
        "kill myself",
        "self harm",
        "end my life",
        "want to die",
        "no reason to live"
    ]

    distress_keywords = [
        "hopeless",
        "worthless",
        "no point",
        "want to disappear"
    ]

    # -------------------------
    # Check HIGH risk phrases
    # -------------------------
    if any(word in text for word in crisis_keywords):
        logger.warning(f"HIGH RISK phrase detected in text: {text}")
        return "high"

    # -------------------------
    # Check MEDIUM risk phrases
    # -------------------------
    if any(word in text for word in distress_keywords):
        logger.warning(f"MEDIUM RISK phrase detected in text: {text}")
        return "medium"

    # -------------------------
    # No safety concern
    # -------------------------
    logger.info("No crisis language detected")
    return "low"


def detect_medium_risk(text: str):
    """
    Detect moderate emotional distress.
    """

    text = text.lower()

    distress_words = [
        "hopeless",
        "worthless",
        "no point",
        "tired of everything",
        "feel empty",
        "can't handle life"
    ]

    if any(word in text for word in distress_words):
        logger.warning(f"Medium distress detected: {text}")
        return True

    logger.info("No medium distress detected")
    return False


def medium_risk_response():
    """
    Response for moderate emotional distress.
    """

    logger.info("Generating medium risk support response")

    return (
        "It sounds like you're going through a really difficult time. "
        "You don't have to deal with everything alone. "
        "Talking with someone you trust might really help. "
        "If things feel overwhelming, you could consider reaching out to "
        "Kiran Mental Health Helpline (1800-599-0019) in India."
    )


def crisis_response():
    """
    Response for severe crisis situations.
    """

    logger.warning("Generating CRISIS support response")

    return (
        "I'm really sorry that you're feeling this much pain. "
        "You don’t have to go through this alone. "
        "It might really help to talk to a real person who can support you right now.\n\n"

        "If you are in India, you can reach out to:\n"
        "• Kiran Mental Health Helpline: 1800-599-0019\n"
        "• iCall Helpline: 9152987821\n\n"

        "You could also consider reaching out to a trusted friend, family member, "
        "teacher, or counselor. You deserve support and care."
    )
