# model.py

from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
import numpy as np
import os
import joblib
from config import SENTENCE_BERT_MODEL

# Load embedding model
embedding_model = SentenceTransformer(SENTENCE_BERT_MODEL)

# Load classifier (or use dummy one if not trained yet)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "intent_classifier_model.pkl")

if os.path.exists(MODEL_PATH):
    classifier = joblib.load(MODEL_PATH)
else:
    # Dummy model: always predicts 'unknown'
    class DummyModel:
        def predict(self, X): return ["unknown"] * len(X)
        def predict_proba(self, X): return [[1.0] + [0.0] * (len(INTENT_LABELS) - 1) for _ in X]

    classifier = DummyModel()

# Corrected version in model.py
def embed_text(text):
    """Encodes a single string of text into a 2D numerical embedding."""
    return embedding_model.encode([text], convert_to_numpy=True)

# Corrected version in model.py
def predict_intent(text):
    """
    Predicts the anomaly status and confidence for a given text.
    Returns: (bool, float) -> (is_anomaly, confidence_score)
    """
    # embed_text() now returns a 2D array with shape (1, 384)
    embedding = embed_text(text)

    # We pass the 2D 'embedding' array directly to the classifier.
    # The [0] is still needed to get the single value out of the result array.
    prediction = classifier.predict(embedding)[0]
    proba = max(classifier.predict_proba(embedding)[0])
    return prediction, proba
