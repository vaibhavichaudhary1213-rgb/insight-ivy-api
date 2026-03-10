from app.logger import logger

analytics_data = {
    "total_users": set(),
    "total_messages": 0,
    "emotion_counts": {},
    "high_risk_count": 0
}


def track_message(user_id: str, emotion: str):

    analytics_data["total_users"].add(user_id)
    analytics_data["total_messages"] += 1

    if emotion not in analytics_data["emotion_counts"]:
        analytics_data["emotion_counts"][emotion] = 0

    analytics_data["emotion_counts"][emotion] += 1


def track_high_risk(user_id: str):

    analytics_data["total_users"].add(user_id)
    analytics_data["high_risk_count"] += 1


def get_summary():

    return {
        "total_users": len(analytics_data["total_users"]),
        "total_messages": analytics_data["total_messages"],
        "emotion_distribution": analytics_data["emotion_counts"],
        "high_risk_count": analytics_data["high_risk_count"]
    }


