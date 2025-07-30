# classify.py

from model import predict_intent
from utils import extract_named_entities, contains_tech_keywords
from config import INTENT_CONFIDENCE_THRESHOLD
import os
import logging
from datetime import datetime
import pandas as pd

# === Logging Setup ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs("logs/classify", exist_ok=True)
log_file = f"logs/classify/{timestamp}.log"

handler = logging.FileHandler(log_file)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# === Message Classification ===
def classify_message_window(messages):
    logger.info("Classifying message window...")
    try:
        combined = " ".join(messages[-5:])
        entities = extract_named_entities(combined)
        keywords = contains_tech_keywords(combined)

        # The model directly predicts the anomaly status.
        predicted_anomaly, confidence = predict_intent(combined)

        # The 'intent' is now a descriptive label we add AFTER prediction.
        intent_label = "anomalous" if predicted_anomaly else "benign"

        # The final anomaly decision is the model's prediction, gated by confidence.
        is_anomaly = bool(predicted_anomaly and confidence > INTENT_CONFIDENCE_THRESHOLD)

        return {
            "intent": intent_label,
            "confidence": round(confidence, 3),
            "keywords": keywords,
            "named_entities": entities,
            "anomaly": is_anomaly
        }
    except Exception as e:
        logger.error(f"Error in classification: {e}")
        return None

# === CSV Classification Test ===
def test_from_csv(csv_file_path, output_file_path):
    logger.info("Running test from CSV...")

    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")
        return

    results = []

    # The 'for' loop block starts here. All lines below must be indented.
    for idx, row in df.iterrows():
        # --- THIS WHOLE BLOCK HAS BEEN RE-INDENTED ---
        logger.info(f"data index: {idx}")

        # This 'if' statement is inside the 'for' loop
        if not isinstance(row['messages'], str):
            # These lines are inside the 'if' statement
            logger.warning(f"Skipping row {idx} due to empty/invalid message.")
            continue  # Skip to the next iteration of the for loop

        # These lines are back inside the 'for' loop
        messages = [msg.strip() for msg in row['messages'].split('|')]
        result = classify_message_window(messages)
        logger.info(f"result:{result}, messages:{messages}")

        # This 'if/else' block is also inside the 'for' loop
        if result:
            results.append({
                "test_case": idx + 1,
                "input_messages": row['messages'],
                "predicted_intent": result['intent'],
                "expected_intent": row.get('intent', ''),
                "predicted_anomaly": result['anomaly'],
                "expected_anomaly": row.get('anomaly', ''),
                "named_entities": ', '.join(result['named_entities']),
                "keywords": ', '.join(result['keywords']),
                "confidence_score": result['confidence']
            })
        else:
            results.append({
                "test_case": idx + 1,
                "input_messages": row['messages'],
                "error": "Classification failed"
            })
    # --- END OF RE-INDENTED BLOCK ---

    # This code runs after the 'for' loop is finished
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_file_path, index=False)
    logger.info(f"✅ Output saved to {output_file_path}")

# === Entry Point ===
if __name__ == "__main__":
    csv_path = r"C:\honeytrapper\intent_classifier\classification_sample_dataset.csv"
    op_path = r"C:\honeytrapper\intent_classifier\classification_results.csv"
    if os.path.exists(csv_path):
        test_from_csv(csv_path, op_path)
    else:
        logger.warning(f"CSV file not found at path: {csv_path}")