def classify_emotion(text: str, intensity: int):

    text_lower = text.lower()

    emotion_keywords = {

    # Sadness
    "sad": ["sad", "down", "unhappy", "upset"],
    "lonely": ["lonely", "alone", "isolated"],
    "hurt": ["hurt", "heartbroken", "pain"],
    "disappointed": ["disappointed", "let down"],
    "grief": ["grief", "loss", "mourning"],

    # Anger
    "angry": ["angry", "mad", "furious"],
    "frustrated": ["frustrated", "annoyed", "irritated"],
    "resentful": ["resentful", "bitter"],

    # Anxiety
    "anxious": ["anxious", "worried", "nervous"],
    "stressed": ["stress", "stressed", "pressure"],
    "overwhelmed": ["overwhelmed", "too much"],
    "burned_out": ["burnout", "burned out", "exhausted"],
    "fearful": ["scared", "afraid", "fear"],
    "insecure": ["insecure", "not good enough", "doubt myself"],

    # Confusion
    "confused": ["confused", "unsure", "uncertain"],
    "lost": ["lost", "directionless"],
    "indecisive": ["indecisive"],

    # Low energy
    "tired": ["tired", "drained"],
    "unmotivated": ["unmotivated", "no motivation"],
    "bored": ["bored"],

    # Positive
    "happy": ["happy", "joy", "glad"],
    "excited": ["excited", "thrilled"],
    "proud": ["proud", "accomplished"],
    "grateful": ["grateful", "thankful"],
    "relieved": ["relieved"],
    "calm": ["calm", "peaceful"],
    "hopeful": ["hopeful", "optimistic"],
    "motivated": ["motivated", "inspired"],
    "confident": ["confident", "self assured"]
}

    positive_emotions = [
        "happy","excited","proud","grateful",
        "relieved","calm","hopeful","motivated","confident"
    ]

    negative_emotions = [
        "sad","lonely","hurt","disappointed","grief",
        "angry","frustrated","resentful",
        "anxious","stressed","overwhelmed","burned_out",
        "fearful","insecure",
        "confused","lost","indecisive",
        "tired","unmotivated","bored"
    ]

    detected_emotions = []

    for emotion, words in emotion_keywords.items():
        if any(word in text_lower for word in words):
            detected_emotions.append(emotion)

    # Determine emotion
    if len(detected_emotions) == 0:
        primary_emotion = "neutral"

    else:
        pos = any(e in positive_emotions for e in detected_emotions)
        neg = any(e in negative_emotions for e in detected_emotions)

        if pos and neg:
            primary_emotion = "mixed"
        else:
            primary_emotion = detected_emotions[0]

    detected_intensity = detect_intensity(text_lower)

    # Clamp user intensity
    intensity = min(max(intensity, 1), 5)

    final_intensity = max(intensity, detected_intensity)

    # Sentiment layer
    if primary_emotion in positive_emotions:
        sentiment = "Positive"
    elif primary_emotion in negative_emotions:
        sentiment = "Negative"
    elif primary_emotion == "mixed":
        sentiment = "Mixed"
    else:
        sentiment = "Neutral"

    context_tags = []

    if any(w in text_lower for w in ["exam","study","assignment","grades"]):
        context_tags.append("Academic stress")

    if any(w in text_lower for w in ["friend","relationship","breakup"]):
        context_tags.append("Social relationships")

    if any(w in text_lower for w in ["future","career","job"]):
        context_tags.append("Career uncertainty")

    if any(w in text_lower for w in ["tired","burnout","exhausted"]):
        context_tags.append("Burnout")

    if any(w in text_lower for w in ["sleep","insomnia","sleeping"]):
        context_tags.append("Sleep issues")

    if any(w in text_lower for w in ["family","parents"]):
        context_tags.append("Family pressure")

    if any(word in text_lower for word in ["money", "fees", "financial"]):
        context_tags.append("Financial stress")

    return {
        "sentiment": sentiment,
        "primary_emotion": primary_emotion,
        "detected_emotions": detected_emotions,
        "intensity": final_intensity,
        "context_tags": context_tags
    }


def detect_intensity(text: str):

    if "extremely" in text or "very" in text:
        return 5
    elif "really" in text:
        return 4
    elif "a little" in text or "slightly" in text:
        return 2
    else:
        return 3





