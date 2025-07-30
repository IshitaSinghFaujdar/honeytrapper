# --- chat_analyzer.py ---
# This is the corrected version for your folder structure.

import sys
import os

# --- FIX FOR THE IMPORT ERROR (Unchanged) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
classifier_path = os.path.join(parent_dir, 'intent_classifier')
if classifier_path not in sys.path:
    sys.path.insert(0, classifier_path)
# --- END OF FIX ---

# --- Import your custom classifier and our logger ---
from classify import classify_message_window
from logger_config import get_logger
logger = get_logger(__name__)


# --- Define ALL Keyword Sets ---
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

# --- NEW: Tech Honeytrap Keywords ---
TECH_HONEYTRAP_KEYWORDS = {
    "recruiter", "hiring", "job offer", "urgent opening", "interview", "salary",
    "confidential project", "nda", "crypto", "token", "presale", "ico", "nft",
    "whitelist", "guaranteed return", "trading bot", "investment opportunity",
    "startup", "co-founder", "proprietary algorithm", "github", "beta access",
    "test my app", "download", "install", ".exe", "run this script"
}
# --- END OF NEW KEYWORDS ---


def analyze_chat_history(message_history: list):
    """
    Analyzes chat history using a hybrid approach with a threat hierarchy:
    1. Calls the custom `classify_message_window` for general anomaly detection.
    2. Performs a specific keyword scan for Sextortion, Tech Honeytraps, and Spam.
    3. Combines results, prioritizing the most severe threats.
    """
    if not message_history:
        logger.warning("analyze_chat_history called with empty message_history.")
        return {
            "spam_confidence_score": 0, "sextortion_confidence_score": 0, "tech_honeytrap_score": 0,
            "primary_intent": "N/A", "keywords_found": {}, "raw_classifier_output": None
        }
    
    logger.info("Starting tiered hybrid chat analysis.")

    # --- Step 1: Perform Keyword Analysis for all sets ---
    full_text = " ".join(message_history).lower()
    found_spam_keywords = {kw for kw in SPAM_KEYWORDS if kw in full_text}
    found_sextortion_keywords = {kw for kw in SEXTORTION_KEYWORDS if kw in full_text}
    found_tech_keywords = {kw for kw in TECH_HONEYTRAP_KEYWORDS if kw in full_text} # --- NEW ---

    # --- Step 2: Call your existing custom classifier ---
    try:
        raw_analysis = classify_message_window(message_history)
        logger.info(f"Custom classifier returned: {raw_analysis}")
    except Exception as e:
        logger.error(f"Error calling classify_message_window: {e}", exc_info=True)
        raw_analysis = None

    # --- Step 3: Combine results and calculate confidence scores ---
    spam_score_from_classifier = 0
    if raw_analysis and raw_analysis.get("anomaly"):
        spam_score_from_classifier = raw_analysis.get("confidence", 0) * 100
        
    spam_confidence = max(spam_score_from_classifier, len(found_spam_keywords) * 10)

    # --- MODIFIED: Tiered confidence calculation for specific threats ---
    sextortion_confidence = 95 if len(found_sextortion_keywords) >= 3 else 60 if len(found_sextortion_keywords) > 0 else 0
    tech_honeytrap_confidence = 85 if len(found_tech_keywords) >= 3 else 50 if len(found_tech_keywords) > 0 else 0

    # --- Step 4: Determine Primary Intent using a Threat Hierarchy ---
    # The order of these checks is CRITICAL. We check for the most severe threat first.
    primary_intent = "Normal Conversation"
    if sextortion_confidence > 50:
        primary_intent = "Sextortion/Blackmail"
    elif tech_honeytrap_confidence > 50:
        primary_intent = "Tech Honeytrap/Scam"
    elif spam_confidence > 50:
        primary_intent = raw_analysis.get("intent", "Spam/Scam") if raw_analysis else "Spam/Scam"
    elif raw_analysis and raw_analysis.get("intent") != "normal":
         primary_intent = raw_analysis.get("intent")

    # --- Step 5: Create the final standardized result format ---
    standardized_result = {
        "spam_confidence_score": min(spam_confidence, 100),
        "sextortion_confidence_score": min(sextortion_confidence, 100),
        "tech_honeytrap_score": min(tech_honeytrap_confidence, 100), # --- NEW ---
        "primary_intent": primary_intent,
        "keywords_found": {
            "spam": list(found_spam_keywords),
            "sextortion": list(found_sextortion_keywords),
            "tech": list(found_tech_keywords) # --- NEW ---
        },
        "raw_classifier_output": raw_analysis
    }
    
    logger.info(f"Final standardized analysis: {standardized_result}")
    return standardized_result