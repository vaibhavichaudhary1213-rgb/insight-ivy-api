import random
from datetime import datetime

kindness_challenges = {
    "campus": [
        "Compliment a classmate genuinely.",
        "Share notes with someone struggling.",
        "Thank a professor for something specific.",
        "Smile at 3 strangers today.",
        "Offer to grab coffee for a friend.",
        "Help someone with directions.",
        "Sit with someone eating alone.",
        "Share your snacks with a friend."
    ],
    "digital": [
        "Send an appreciation text to someone.",
        "Leave a positive comment online.",
        "Forgive someone silently in your heart.",
        "Check on a friend you haven't spoken to in weeks.",
        "Share a helpful resource with your study group.",
        "Send a meme to make someone laugh.",
        "Leave a good review for a small business.",
        "Message a former teacher who helped you."
    ],
    "self_kindness": [
        "Talk to yourself like you would to a friend.",
        "Take a 10-minute guilt-free break.",
        "Drink water and stretch right now.",
        "Write a letter to your future self.",
        "Say 'no' to something without explaining.",
        "Do something that brings you joy for 15 minutes.",
        "Forgive yourself for a small mistake.",
        "Look in the mirror and say something nice."
    ],
    "micro_impact": [
        "Donate a small amount to a cause online.",
        "Pick up litter on campus.",
        "Hold a door open for someone.",
        "Say thank you more intentionally today.",
        "Let someone go ahead of you in line.",
        "Water a plant.",
        "Leave a kind note somewhere.",
        "Return a shopping cart for someone."
    ]
}

kindness_history = {}

def get_kindness_challenge(category="all"):
    """Get a random kindness challenge from specified category"""
    if category == "all":
        all_challenges = []
        for cat in kindness_challenges.values():
            all_challenges.extend(cat)
        return random.choice(all_challenges)
    elif category in kindness_challenges:
        return random.choice(kindness_challenges[category])
    else:
        return random.choice(kindness_challenges["campus"])  # Default

def complete_kindness_challenge(user_id: str, challenge: str):
    """Track completed kindness challenges"""
    if user_id not in kindness_history:
        kindness_history[user_id] = []
    
    entry = {
        "challenge": challenge,
        "completed_at": datetime.now().isoformat()
    }
    kindness_history[user_id].append(entry)
    
    # Track milestones
    total = len(kindness_history[user_id])
    if total == 1:
        return "🌈 First kindness challenge completed! The world is brighter because of you."
    elif total == 5:
        return "🌟 5 acts of kindness! You're spreading so much light!"
    elif total == 10:
        return "💫 10 kindness challenges! You're officially a kindness superstar!"
    elif total % 10 == 0:
        return f"🎉 {total} acts of kindness! Keep shining!"
    
    return entry

def get_kindness_stats(user_id: str):
    """Get kindness challenge statistics"""
    history = kindness_history.get(user_id, [])
    
    # Group by category
    stats = {
        "total": len(history),
        "by_category": {},
        "recent": history[-5:] if history else []
    }
    
    for entry in history:
        challenge = entry["challenge"]
        category = None
        for cat, challenges in kindness_challenges.items():
            if challenge in challenges:
                category = cat
                break
        
        if category:
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
    
    return stats