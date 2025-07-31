# --- ai_detector.py (Now includes Mimicry Detection) ---

import re
from collections import Counter

# --- Heuristic 1: Overly Formal or "Corporate" Language (Unchanged) ---
AI_FORMAL_PHRASES = [
    'i can assist you', 'i can help you', 'furthermore', 'in conclusion', 'it is important to note',
    'i am just an ai', 'as an ai', 'as a language model', 'i do not have personal',
    'i am unable to', 'my purpose is to', 'i can provide you with'
]

# --- Heuristic 2: Lack of Human "Flavor" (Unchanged) ---
HUMAN_SLANG_FILLER_WORDS = [
    'lol', 'lmao', 'omg', 'btw', 'tbh', 'imo', 'fr', 'no cap',
    'like,', 'you know,', 'i mean,', 'kinda', 'sorta', 'um,', 'uh,'
]

def analyze_for_ai_patterns(message: str) -> dict:
    """
    Analyzes a single message for signs of being AI-generated.
    (This function remains exactly the same)
    """
    score = 0
    reasons = []
    text = message.lower()

    # (Logic for AI detection is unchanged)
    for phrase in AI_FORMAL_PHRASES:
        if phrase in text:
            score += 50
            reasons.append(f"Contains classic AI phrase: '{phrase}'")

    contractions = ["'m", "'re", "'s", "'ve", "'d", "'ll", "n't"]
    has_contractions = any(c in text for c in contractions)
    if len(text.split()) > 15 and not has_contractions:
        score += 15
        reasons.append("Long sentences with perfect grammar and no contractions.")

    has_human_filler = any(word in text for word in HUMAN_SLANG_FILLER_WORDS)
    if len(text.split()) > 10 and not has_human_filler:
        score += 10
        reasons.append("Lacks common human filler words or slang.")
        
    sentences = [s for s in re.split(r'[.!?]', text) if s]
    if len(sentences) > 2:
        lengths = [len(s.split()) for s in sentences]
        mean = sum(lengths) / len(lengths)
        variance = sum([((x - mean) ** 2) for x in lengths]) / len(lengths)
        std_dev = variance ** 0.5
        if std_dev < 2.0:
            score += 20
            reasons.append("Unnaturally consistent sentence length, a common AI trait.")

    is_likely_ai = score > 40

    return {
        "is_likely_ai": is_likely_ai,
        "score": score,
        "reasons": reasons
    }

# --- NEW FEATURE: DEEP BEHAVIORAL MIMICRY DETECTION ---
def analyze_for_deep_mimicry(user_bot_messages: list[str], scammer_messages: list[str]) -> dict:
    """
    Analyzes for signs of deep behavioral mimicry.
    
    Looks for the scammer re-using specific, non-common words or phrases
    that the user's bot ("Alex") introduced into the conversation.
    
    Returns a dictionary indicating if mimicry is detected and what phrases were mimicked.
    """
    # Don't run analysis if there's not enough conversation history
    if not user_bot_messages or not scammer_messages:
        return {"is_mimicking": False, "mimicked_phrases": []}
        
    # Get unique, non-trivial words from the user's bot ("Alex")
    # We look for words of 5 or more letters to filter out common words like "the", "and", "you".
    user_bot_words = set(re.findall(r'\b\w{5,}\b', " ".join(user_bot_messages).lower()))
    
    # Combine all of the scammer's messages into a single block of text
    scammer_text = " ".join(scammer_messages).lower()
    
    mimicked_phrases = []
    # Check if the scammer is re-using the user's bot's unique words
    for word in user_bot_words:
        if word in scammer_text:
            mimicked_phrases.append(word)
    
    # Set a threshold for detection. If the scammer mirrors more than 4 unique words,
    # it's a strong sign of intentional mimicry to build false rapport.
    is_mimicking = len(mimicked_phrases) > 4
    
    return {
        "is_mimicking": is_mimicking,
        "mimicked_phrases": mimicked_phrases
    }