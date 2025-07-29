# classify.py

from model import predict_intent
from utils import extract_named_entities, contains_tech_keywords
from config import INTENT_CONFIDENCE_THRESHOLD
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
#this is log initializaton
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs("logs/classify", exist_ok=True)
log_file = f"logs/classify/{timestamp}.log"

handler=logging.FileHandler(log_file) #trying to save log file with date  and time, idk if that will work. Let's see
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def classify_message_window(messages):
    logger.info("classify message function")
    try:
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
    except Exception as e:
        logger.error(f"Error: {e}")
# For testing
if __name__ == "__main__":
    logger.info("main function")
    sample_messages = [
        "Hey cutie 😊",
        "What do you do?",
        "Do you work in tech?",
        "Can I see your GitHub repo?",
        "Do you have access to any production server?"
    ]
    logger.info(f"messages: {sample_messages}")
    result = classify_message_window(sample_messages)
    logger.info(f"result: {result}")
    print(result)
