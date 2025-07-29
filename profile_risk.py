# risk_model_training.py

import pandas as pd
import joblib
import logging
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from transformers import pipeline as hf_pipeline

# -----------------------------------------------
# 📜 Setup Logging
# -----------------------------------------------
logging.basicConfig(
    filename='D:/honeytrap/risk_model_training.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    print(msg)
    logging.info(msg)

# -----------------------------------------------
# 📥 Load and Preprocess Data
# -----------------------------------------------
def load_data(csv_path):
    log("Loading data...")
    df = pd.read_csv(csv_path)
    log(f"Data loaded: {df.shape[0]} records, {df.shape[1]} columns.")
    return df

def preprocess_data(df):
    log("Preprocessing data...")

    # Coerce types
    df['is_private'] = df['is_private'].astype(str)
    df['is_verified'] = df['is_verified'].astype(str)
    df['photo_source'] = df['photo_source'].astype(str)

    # Add sentiment score for bio
    log("Running sentiment analysis on bios...")
    sentiment_model = hf_pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
    df['bio_sentiment_score'] = df['bio'].apply(lambda text: 1 if sentiment_model(text)[0]['label'] == 'POSITIVE' else 0)
    
    log("Preprocessing complete.")
    return df

# -----------------------------------------------
# 🧠 Train Model
# -----------------------------------------------
def train_model(df):
    log("Training model...")

    features = ['followers', 'following', 'account_age_days', 'is_private', 'is_verified', 'photo_source', 'bio_sentiment_score']
    target = 'risk_label'

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    numeric_features = ['followers', 'following', 'account_age_days', 'bio_sentiment_score']
    categorical_features = ['is_private', 'is_verified', 'photo_source']

    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])

    clf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    clf_pipeline.fit(X_train, y_train)

    log("Model training complete.")
    return clf_pipeline, X_test, y_test

# -----------------------------------------------
# 🧾 Evaluation
# -----------------------------------------------
def evaluate_model(model, X_test, y_test):
    log("Evaluating model...")
    y_pred = model.predict(X_test)

    report = classification_report(y_test, y_pred)
    matrix = confusion_matrix(y_test, y_pred)

    log("Classification Report:\n" + report)
    log("Confusion Matrix:\n" + str(matrix))

# -----------------------------------------------
# 💾 Save Model
# -----------------------------------------------
def save_model(model, path):
    joblib.dump(model, path)
    log(f"Model saved to {path}")

# -----------------------------------------------
# 🚀 MAIN
# -----------------------------------------------
def main():
    log("==== Risk Model Training Started ====")

    csv_path = "D:/honeytrap/simulated_instagram_profiles.csv"
    model_path = "D:/honeytrap/risk_model.pkl"

    df = load_data(csv_path)
    df = preprocess_data(df)
    model, X_test, y_test = train_model(df)
    evaluate_model(model, X_test, y_test)
    save_model(model, model_path)

    log("==== Risk Model Training Completed ====")

if __name__ == "__main__":
    main()
