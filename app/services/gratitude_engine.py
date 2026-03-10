import random

gratitude_prompts = [
    "Name one small thing that made you smile today.",
    "Who is someone you're grateful for right now?",
    "What is one comfort in your life you appreciate?",
    "What is something your past self would be proud of?"
]

def generate_gratitude():
    return random.choice(gratitude_prompts)