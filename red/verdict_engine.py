# --- verdict_engine.py ---
# Module 3 of Project Sentinel

def calculate_final_verdict(profile_risk_score: int, chat_confidence_score: float):
    """
    Calculates a final verdict score by combining profile and chat analysis.
    Args:
        profile_risk_score: The score from the profile analyzer (0-10).
        chat_confidence_score: The confidence score from the chat analyzer (0-100).
        
    Returns:
        A final weighted score (0-100).
    """
    # Convert profile score (0-10) to a 0-100 scale for weighting.
    profile_score_100 = profile_risk_score * 10
    
    # Define weights. Chat content is often more revealing, so we give it more weight.
    CHAT_WEIGHT = 0.70  # 70% importance
    PROFILE_WEIGHT = 0.30  # 30% importance
    
    final_score = (chat_confidence_score * CHAT_WEIGHT) + (profile_score_100 * PROFILE_WEIGHT)
    
    # Ensure the score does not exceed 100.
    return min(final_score, 100)