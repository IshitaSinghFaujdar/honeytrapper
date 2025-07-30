# --- chat_analyzer.py (Corrected Indentation) ---

import sys
import os

# --- FIX FOR THE IMPORT ERROR (Unchanged) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
classifier_path = os.path.join(parent_dir, 'intent_classifier')
if classifier_path not in sys.path:
    sys.path.insert(0, classifier_path)

# --- Import your custom classifier, logger, and psychological analyzer ---
from classify import classify_message_window
from logger_config import get_logger
from psychological_analyzer import analyze_psychological_patterns

logger = get_logger(__name__)

# --- Keyword Sets (Unchanged) ---
SPAM_KEYWORDS = {
    "free", "winner", "claim", "prize", "congratulations", "urgent", "investment",
    "guaranteed", "profit", "click here", "limited time", "act now", "risk-free",
    "sugar daddy", "allowance" , "security", "defense","india","bank", "bomb"
}
SEXTORTION_KEYWORDS = {
    "expose", "leak", "ruin", "post", "share", "family", "friends", "employer",
    "shame", "humiliate", "destroy your life", "private", "intimate", "explicit",
    "nude", "naked", "photos", "video", "webcam", "compromising", "pay", "money",
    "payment", "bitcoin", "gift card", "unless", "or else", "last chance", "immediately"
}
TECH_HONEYTRAP_KEYWORDS = {
    "recruiter", "hiring", "job offer", "urgent opening", "interview", "salary",
    "confidential project", "nda", "crypto", "token", "presale", "ico", "nft",
    "whitelist", "guaranteed return", "trading bot", "investment opportunity",
    "startup", "co-founder", "proprietary algorithm", "github", "beta access",
    "test my app", "download", "install", ".exe", "run this script"
}


def analyze_chat_history(message_history: list):
    """
    Analyzes chat history using a hybrid approach with a threat hierarchy.
    Now includes a psychological profiling layer.
    """
    # --- THIS IS THE CORRECTED BLOCK ---
    if not message_history:
        logger.warning("analyze_chat_history called with empty message_history. Returning default.")
        # This indented block tells Python what to do if the condition is true.
        return {
            "spam_confidence_score": 0,
            "sextortion_confidence_score": 0,
            "tech_honeytrap_score": 0,
            "primary_intent": "N/A",
            "keywords_found": {"spam": [], "sextortion": [], "tech": []},
            "psychological_analysis": {"total_risk_score": 0},
            "raw_classifier_output": None
        }
    # --- END OF CORRECTION ---

    logger.info("Starting tiered hybrid chat analysis.")

    # --- Step 1 & 2 (Unchanged) ---
    full_text = " ".join(message_history).lower()
    found_spam_keywords = {kw for kw in SPAM_KEYWORDS if kw in full_text}
    found_sextortion_keywords = {kw for kw in SEXTORTION_KEYWORDS if kw in full_text}
    found_tech_keywords = {kw for kw in TECH_HONEYTRAP_KEYWORDS if kw in full_text}
    
    try:
        raw_analysis = classify_message_window(message_history)
        logger.info(f"Custom classifier returned: {raw_analysis}")
    except Exception as e:
        logger.error(f"Error calling classify_message_window: {e}", exc_info=True)
        raw_analysis = None
        
    # --- Step 3 - Perform Psychological Analysis ---
    logger.info("Performing psychological pattern analysis...")
    psych_analysis = analyze_psychological_patterns(message_history)
    psych_total_score = psych_analysis.get('total_risk_score', 0)
    logger.info(f"Psychological analysis returned total risk score: {psych_total_score}")

    # --- Step 4: Combine results and calculate confidence scores (MODIFIED) ---
    spam_score_from_classifier = 0
    if raw_analysis and raw_analysis.get("anomaly"):
        spam_score_from_classifier = raw_analysis.get("confidence", 0) * 100
        
    spam_confidence = max(spam_score_from_classifier, len(found_spam_keywords) * 10)
    sextortion_confidence = 95 if len(found_sextortion_keywords) >= 3 else 60 if len(found_sextortion_keywords) > 0 else 0
    tech_honeytrap_confidence = 85 if len(found_tech_keywords) >= 3 else 50 if len(found_tech_keywords) > 0 else 0

    # Boost confidence scores based on psychological risk
    if psych_total_score > 0:
        sextortion_confidence += psych_total_score * 0.2
        tech_honeytrap_confidence += psych_total_score * 0.2
        spam_confidence += psych_total_score * 0.1

    # --- Step 5: Determine Primary Intent (Unchanged) ---
    primary_intent = "Normal Conversation"
    if sextortion_confidence > 50:
        primary_intent = "Sextortion/Blackmail"
    elif tech_honeytrap_confidence > 50:
        primary_intent = "Tech Honeytrap/Scam"
    elif spam_confidence > 50:
        primary_intent = raw_analysis.get("intent", "Spam/Scam") if raw_analysis else "Spam/Scam"
    elif raw_analysis and raw_analysis.get("intent") != "normal":
         primary_intent = raw_analysis.get("intent")

    # --- Step 6: Create the final standardized result format (Unchanged) ---
    standardized_result = {
        "spam_confidence_score": min(spam_confidence, 100),
        "sextortion_confidence_score": min(sextortion_confidence, 100),
        "tech_honeytrap_score": min(tech_honeytrap_confidence, 100),
        "primary_intent": primary_intent,
        "keywords_found": {
            "spam": list(found_spam_keywords),
            "sextortion": list(found_sextortion_keywords),
            "tech": list(found_tech_keywords)
        },
        "psychological_analysis": psych_analysis,
        "raw_classifier_output": raw_analysis
    }
    
    logger.info(f"Final standardized analysis: {standardized_result}")
    return standardized_result