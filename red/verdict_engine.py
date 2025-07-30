# In verdict_engine.py

def calculate_final_verdict(profile_risk_score, chat_analysis_results):
    spam_score = chat_analysis_results.get("spam_confidence_score", 0)
    sextortion_score = chat_analysis_results.get("sextortion_confidence_score", 0)
    tech_score = chat_analysis_results.get("tech_honeytrap_score", 0) # --- NEW ---

    profile_risk_percent = profile_risk_score * 10
    
    spam_verdict = (0.3 * profile_risk_percent) + (0.7 * spam_score)
    tech_verdict = (0.3 * profile_risk_percent) + (0.7 * tech_score) # --- NEW ---
    sextortion_verdict = (0.2 * profile_risk_percent) + (0.8 * sextortion_score) # Highest weight

    # Final verdict is the highest of ALL potential threats
    final_verdict = max(spam_verdict, tech_verdict, sextortion_verdict) # --- MODIFIED ---
    
    return min(final_verdict, 100)