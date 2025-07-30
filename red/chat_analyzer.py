# --- chat_analyzer.py ---
# This is the corrected version for your folder structure.

import sys
import os

# --- FIX FOR THE IMPORT ERROR ---
# Get the directory of the current file (e.g., C:\honeytrapper\red)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (e.g., C:\honeytrapper)
parent_dir = os.path.dirname(current_dir)

# Construct the full path to your classifier's folder
# This will be 'C:\honeytrapper\intent_classifiers'
classifier_path = os.path.join(parent_dir, 'intent_classifier')

# Add the classifier's directory to Python's search path
if classifier_path not in sys.path:
    sys.path.insert(0, classifier_path)
# --- END OF FIX ---


# --- DEBUGGING LINE (Optional but helpful) ---
# This will print out the folder we just added.
# You can remove this after it works.
print(f"DEBUG: Added '{classifier_path}' to Python's search paths.")
# --- END OF DEBUGGING LINE ---


# Now, this import will work because Python is looking inside the 'intent_classifiers' folder.
from intent_classifier.classify import classify_message_window


def analyze_chat_history(message_history: list):
    """
    The bridge function that calls your classifier and standardizes the output.
    """
    if not message_history:
        return {
            "spam_confidence_score": 0,
            "intent": "N/A",
            "keywords": [],
            "raw_output": None
        }

    # Call your existing function
    raw_analysis = classify_message_window(message_history)

    if not raw_analysis:
        return {
            "spam_confidence_score": 0,
            "intent": "Error in classification",
            "keywords": [],
            "raw_output": None
        }

    spam_confidence = 0
    if raw_analysis.get("anomaly"):
        spam_confidence = raw_analysis.get("confidence", 0) * 100

    standardized_result = {
        "spam_confidence_score": spam_confidence,
        "intent": raw_analysis.get("intent", "unknown"),
        "keywords": raw_analysis.get("keywords", []),
        "raw_output": raw_analysis
    }

    return standardized_result