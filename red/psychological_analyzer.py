# --- psychological_analyzer.py ---
# Module for detecting psychological manipulation tactics in chat logs.

import re

# --- Tactic 1: Love Bombing Detection ---
LOVE_BOMBING_KEYWORDS = [
    'soulmate', 'perfect for me', 'destiny', 'fate', 'meant to be', 'my everything',
    'never felt this way', 'so fast', 'so quickly', 'can\'t live without you', 'my one and only',
    'future together', 'our future', 'dream of you', 'always thinking of you', 'perfect match'
]

def detect_love_bombing(messages: list[str]) -> (int, list[str]):
    """
    Detects signs of love bombing. Looks for excessive praise and future-faking.
    Returns a score and a list of triggering messages.
    """
    score = 0
    evidence = []
    # Combine all messages into one text block for easier searching
    full_text = " ".join(messages).lower()
    
    for keyword in LOVE_BOMBING_KEYWORDS:
        if keyword in full_text:
            score += 15 # Each keyword adds a significant score
            # Find the original message that contained this keyword
            for msg in messages:
                if keyword in msg.lower() and msg not in evidence:
                    evidence.append(msg)
    
    # Check for excessive use of "I love you" or "love you" very early
    if len(messages) < 20 and full_text.count("love you") > 2:
        score += 20
        evidence.append("Multiple declarations of 'love' in a very short conversation.")

    return score, evidence

# --- Tactic 2: Urgency & Pressure Detection ---
URGENCY_KEYWORDS = [
    'act now', 'right now', 'immediately', 'quick', 'hurry', 'don\'t wait', 'last chance',
    'today only', 'before it\'s too late', 'limited time', 'do it now', 'need you to',
    'let\'s move to', 'telegram', 'whatsapp', 'signal', 'talk off this app'
]

def detect_urgency(messages: list[str]) -> (int, list[str]):
    """
    Detects signs of pressure tactics and attempts to move to unmonitored platforms.
    Returns a score and a list of triggering messages.
    """
    score = 0
    evidence = []
    full_text = " ".join(messages).lower()

    for keyword in URGENCY_KEYWORDS:
        if keyword in full_text:
            score += 20
            for msg in messages:
                if keyword in msg.lower() and msg not in evidence:
                    evidence.append(msg)
    
    return score, evidence

# --- Tactic 3: Secrecy & Isolation ---
SECRECY_KEYWORDS = [
    'don\'t tell anyone', 'keep this between us', 'our secret', 'nobody would understand',
    'they won\'t understand', 'your friends are wrong', 'your family doesn\'t get it', 'only I understand you'
]

def detect_secrecy(messages: list[str]) -> (int, list[str]):
    """
    Detects attempts to create secrecy and isolate the user.
    Returns a score and a list of triggering messages.
    """
    score = 0
    evidence = []
    full_text = " ".join(messages).lower()

    for keyword in SECRECY_KEYWORDS:
        if keyword in full_text:
            score += 30 # Secrecy is a major red flag
            for msg in messages:
                if keyword in msg.lower() and msg not in evidence:
                    evidence.append(msg)

    return score, evidence


# --- Main Orchestrator Function ---
def analyze_psychological_patterns(messages: list[str]) -> dict:
    """
    Runs all psychological tactic detectors and compiles the results.
    Returns a dictionary with tactic names, scores, and evidence.
    """
    results = {}
    total_score = 0

    # Run each detector
    lb_score, lb_evidence = detect_love_bombing(messages)
    if lb_evidence:
        results['Love Bombing'] = {'score': lb_score, 'evidence': lb_evidence}
        total_score += lb_score

    urgency_score, urgency_evidence = detect_urgency(messages)
    if urgency_evidence:
        results['Urgency & Pressure'] = {'score': urgency_score, 'evidence': urgency_evidence}
        total_score += urgency_score

    secrecy_score, secrecy_evidence = detect_secrecy(messages)
    if secrecy_evidence:
        results['Secrecy & Isolation'] = {'score': secrecy_score, 'evidence': secrecy_evidence}
        total_score += secrecy_score
    
    # We can add a "Total Psychological Risk Score" to be used later
    results['total_risk_score'] = total_score
    
    return results