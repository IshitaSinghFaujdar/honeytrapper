# config.py

# List of technical keywords to flag for secondary analysis.
# Stored in lowercase for case-insensitive matching.
TECH_KEYWORDS = [
    "api key", "token", "access", "database", "ip", "admin", "ssh", "cloud", 
    "server", "github", "repo", "vpn", "proxy", "2fa", "aws", "docker", 
    "deployment", "production server", "internal data", "clients", 
    "system access", "cybersecurity"
]

# Confidence threshold for flagging an anomaly.
# Tune this value after reviewing model performance.
INTENT_CONFIDENCE_THRESHOLD = 0.85

# Pre-trained Sentence-BERT model name for generating embeddings.
SENTENCE_BERT_MODEL = 'all-MiniLM-L6-v2'

# --- The primary labels our BINARY model will predict ---
# The model is trained on the 'anomaly' column, which is boolean.
# This makes it clear our model predicts one of these two states.
ANOMALY_LABELS = {
    False: "benign",
    True: "anomalous"
}

# The original intent labels from the dataset can be kept for reference
# or for a future multi-class model, but they are not used by the current
# binary anomaly detection model.
DATASET_INTENT_LABELS = ["flirty", "casual", "technical", "probing"]