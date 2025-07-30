# train.py

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import numpy as np
import os
from config import SENTENCE_BERT_MODEL # Make sure config.py is set up

print("Loading dataset...")
# Make sure your CSV file is accessible
df = pd.read_csv('classification_sample_dataset.csv')
df.dropna(subset=['messages'], inplace=True) # Remove rows with no messages

# --- DECIDE ON YOUR TARGET ---
# For honeytrap detection, 'anomaly' is the best target.
# If you wanted to predict 'flirty', 'casual', etc., you would use 'intent'.
X = df['messages']
y = df['anomaly']  # Using the True/False anomaly column

print(f"Loaded {len(df)} samples.")
print("Target distribution:\n", y.value_counts())

# 1. Create Embeddings with SentenceTransformer
print(f"\nLoading SentenceTransformer model: {SENTENCE_BERT_MODEL}")
embedding_model = SentenceTransformer(SENTENCE_BERT_MODEL)

print("Creating embeddings for all messages... (This may take a while)")
# .encode() is highly optimized for creating embeddings in batches
X_embeddings = embedding_model.encode(X.tolist(), show_progress_bar=True)
print("Embeddings created successfully. Shape:", X_embeddings.shape)

# 2. Split Data for Training and Testing
X_train, X_test, y_train, y_test = train_test_split(
    X_embeddings, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Train the Classifier
print("\nTraining the Logistic Regression classifier...")
# Increased max_iter for convergence with complex embeddings
classifier = LogisticRegression(solver='liblinear', random_state=42, max_iter=1000)
classifier.fit(X_train, y_train)
print("Training complete.")

# 4. Evaluate the Model
print("\n--- Model Evaluation ---")
y_pred = classifier.predict(X_test)
print(classification_report(y_test, y_pred))

# 5. Save the Trained Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "intent_classifier_model.pkl")
print(f"\nSaving trained model to: {MODEL_PATH}")
joblib.dump(classifier, MODEL_PATH)
print("Model saved successfully!")

# You also need to save the mapping from model output to labels
# For a boolean 'anomaly' target, the labels are simple: False, True
# For a multi-class 'intent' target, you'd save classifier.classes_
# This ensures your `model.py` knows what the model's outputs (0, 1) mean.
# For simplicity, we'll assume your `model.py` can handle boolean outputs directly.