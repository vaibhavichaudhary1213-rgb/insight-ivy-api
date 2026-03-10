import random

kindness_challenges = [
    "Send a kind message to a friend.",
    "Smile at someone today.",
    "Help someone with a small task.",
    "Compliment someone genuinely."
]

def generate_kindness():
    return random.choice(kindness_challenges)
