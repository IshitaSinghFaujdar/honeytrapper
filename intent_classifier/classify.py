# classify.py

from model import predict_intent
from utils import extract_named_entities, contains_tech_keywords
from config import INTENT_CONFIDENCE_THRESHOLD

def classify_message_window(messages):
    combined = " ".join(messages[-5:])  # Use last 5 messages
    entities = extract_named_entities(combined)
    keywords = contains_tech_keywords(combined)
    
    intent, confidence = predict_intent(combined)
    anomaly = (intent == "probing" or intent == "technical") and confidence > INTENT_CONFIDENCE_THRESHOLD

    return {
        "intent": intent,
        "confidence": round(confidence, 3),
        "keywords": keywords,
        "named_entities": entities,
        "anomaly": anomaly
    }

# For testing
if __name__ == "__main__":
    sample_messages = [
        "Hey cutie 😊",
        "What do you do?",
        "Do you work in tech?",
        "Can I see your GitHub repo?",
        "Do you have access to any production server?"
    ]
    result = classify_message_window(sample_messages)
    print(result)
