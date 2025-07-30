# --- verdict_engine.py (Updated for Hybrid Analysis) ---

def calculate_final_verdict(profile_risk_score: int, chat_analysis: dict):
    """
    Calculates a final verdict based on the comprehensive chat analysis dictionary
    which now includes psychological profiling data.
    """
    profile_score_100 = profile_risk_score * 10
    
    # Extract the psychological risk score from the embedded dictionary
    psych_risk_score = chat_analysis.get('psychological_analysis', {}).get('total_risk_score', 0)
    
    # Get the confidence score of the primary threat (your logic is good here)
    primary_intent = chat_analysis.get('primary_intent', 'Normal Conversation')
    if primary_intent == 'Sextortion/Blackmail':
        primary_threat_score = chat_analysis.get('sextortion_confidence_score', 0)
    elif primary_intent == 'Tech Honeytrap/Scam':
        primary_threat_score = chat_analysis.get('tech_honeytrap_score', 0)
    else: # General Spam or Normal
        primary_threat_score = chat_analysis.get('spam_confidence_score', 0)

    # Define weights - let's give the primary detected threat the most weight
    PRIMARY_THREAT_WEIGHT = 0.60
    PROFILE_WEIGHT = 0.20
    PSYCH_WEIGHT = 0.20 # The psych score's main job was boosting confidence; it has a smaller direct impact here.
    
    # Cap the raw psychological score to prevent it from dominating the final verdict
    capped_psych_score = min(psych_risk_score, 100)
    
    final_score = (
        (primary_threat_score * PRIMARY_THREAT_WEIGHT) + 
        (profile_score_100 * PROFILE_WEIGHT) +
        (capped_psych_score * PSYCH_WEIGHT)
    )
    
    return min(final_score, 100)