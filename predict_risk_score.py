# predict_risk_score.py

import pandas as pd
import joblib
import logging
from transformers import pipeline as hf_pipeline

# -----------------------------------------------
# 📜 Setup Logging (Optional, for this script)
# -----------------------------------------------
# You might want to log predictions or errors in a real application.
# For this simple script, we'll just print to console.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg, level=logging.INFO):
    """Simple logging function that also prints to console."""
    print(msg)
    if level == logging.INFO:
        logging.info(msg)
    elif level == logging.ERROR:
        logging.error(msg)

# -----------------------------------------------
# 🧠 Load Trained Model
# -----------------------------------------------
def load_trained_model(model_path):
    """
    Loads the pre-trained risk model from the specified path.
    """
    try:
        log(f"Loading model from {model_path}...")
        model = joblib.load(model_path)
        log("Model loaded successfully.")
        return model
    except FileNotFoundError:
        log(f"Error: Model file not found at {model_path}. Please ensure the path is correct.", level=logging.ERROR)
        return None
    except Exception as e:
        log(f"Error loading model: {e}", level=logging.ERROR)
        return None

# -----------------------------------------------
# ⚙️ Preprocess New Data for Prediction
# -----------------------------------------------
# Initialize sentiment model once globally to avoid re-loading for each prediction
try:
    log("Initializing sentiment analysis model (this may take a moment)...")
    sentiment_model = hf_pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
    log("Sentiment analysis model initialized.")
except Exception as e:
    log(f"Could not load sentiment analysis model: {e}. Predictions involving 'bio' might fail.", level=logging.ERROR)
    sentiment_model = None # Set to None if loading fails

def preprocess_new_profile(profile_data):
    """
    Preprocesses a single new profile's data to match the model's expected input format.
    This includes type coercion and sentiment analysis on the bio.

    Args:
        profile_data (dict): A dictionary containing the features of a new profile.
                             Example: {
                                 'followers': 120,
                                 'following': 60,
                                 'account_age_days': 200,
                                 'is_private': False,
                                 'is_verified': False,
                                 'photo_source': 'profile_pic',
                                 'bio': 'Love to travel and explore new places!'
                             }
    Returns:
        pd.DataFrame: A DataFrame with the preprocessed features, ready for prediction.
                      Returns None if sentiment model fails.
    """
    # Convert the single profile dictionary to a pandas DataFrame
    df = pd.DataFrame([profile_data])

    # Coerce types (as done in training)
    df['is_private'] = df['is_private'].astype(str)
    df['is_verified'] = df['is_verified'].astype(str)
    df['photo_source'] = df['photo_source'].astype(str)

    # Add sentiment score for bio (as done in training)
    if sentiment_model:
        log("Running sentiment analysis on new profile bio...")
        df['bio_sentiment_score'] = df['bio'].apply(lambda text: 1 if sentiment_model(text)[0]['label'] == 'POSITIVE' else 0)
    else:
        log("Sentiment model not available. Cannot process 'bio_sentiment_score'.", level=logging.ERROR)
        return None # Or handle this case based on your model's tolerance for missing features

    # Drop the original 'bio' column as it's not a feature for the model pipeline
    df = df.drop(columns=['bio'])

    # Ensure column order matches the training features.
    # This is crucial for ColumnTransformer in the pipeline.
    # The order must be exactly as in your `train_model` function:
    # ['followers', 'following', 'account_age_days', 'is_private', 'is_verified', 'photo_source', 'bio_sentiment_score']
    expected_features_order = [
        'followers', 'following', 'account_age_days',
        'is_private', 'is_verified', 'photo_source', 'bio_sentiment_score'
    ]
    
    # Reorder columns to match the training data's feature order
    # This will also add any missing columns (e.g., if a feature was not provided in profile_data)
    # and fill them with NaN, which the preprocessor might handle or raise an error for.
    # It's better to ensure all expected features are present in profile_data.
    for feature in expected_features_order:
        if feature not in df.columns:
            # This should ideally not happen if profile_data is complete.
            # For categorical features, you might need a default value.
            # For numeric, NaN is often handled by StandardScaler.
            df[feature] = None # Or a suitable default based on your data

    df = df[expected_features_order]
    
    log("New profile data preprocessed.")
    return df

# -----------------------------------------------
# 🚀 Main Prediction Logic
# -----------------------------------------------
def predict_risk(profile_data, model_path="D:/honeytrap/risk_model.pkl"):
    """
    Loads the model and predicts the risk label for a given profile.

    Args:
        profile_data (dict): A dictionary containing the features of a new profile.
        model_path (str): The path to the saved model file.

    Returns:
        int or None: The predicted risk label (0 for low risk, 1 for high risk),
                     or None if prediction fails.
    """
    model = load_trained_model(model_path)
    if model is None:
        return None

    processed_data = preprocess_new_profile(profile_data)
    if processed_data is None:
        return None

    try:
        log("Making prediction...")
        prediction = model.predict(processed_data)
        # If your model also provides probabilities, you can get them using predict_proba
        # probabilities = model.predict_proba(processed_data)
        # log(f"Prediction probabilities: {probabilities}")

        risk_label = int(prediction[0]) # Convert numpy.int64 to standard int
        log(f"Prediction successful. Risk Label: {risk_label}")
        return risk_label
    except Exception as e:
        log(f"Error during prediction: {e}", level=logging.ERROR)
        return None

# -----------------------------------------------
# 💡 Example Usage
# -----------------------------------------------
if __name__ == "__main__":
    log("==== Risk Prediction Script Started ====")

    # Define a sample new Instagram profile
    sample_profile_high_risk = {
        'followers': 15,
        'following': 300,
        'account_age_days': 50,
        'is_private': True,
        'is_verified': False,
        'photo_source': 'stock',
        'bio': 'Spamming accounts for fun. Follow me for tricks!'
    }

    sample_profile_low_risk = {
        'followers': 1500,
        'following': 200,
        'account_age_days': 700,
        'is_private': False,
        'is_verified': False,
        'photo_source': 'ai',
        'bio': 'Travel enthusiast and photographer. Sharing my journey!'
    }

    # Predict for the high-risk profile
    log("\n--- Predicting for a potential HIGH-RISK profile ---")
    predicted_risk_high = predict_risk(sample_profile_high_risk)
    if predicted_risk_high is not None:
        risk_status = "HIGH RISK" if predicted_risk_high == 1 else "LOW RISK"
        log(f"Predicted Risk Status: {risk_status}")

    # Predict for the low-risk profile
    log("\n--- Predicting for a potential LOW-RISK profile ---")
    predicted_risk_low = predict_risk(sample_profile_low_risk)
    if predicted_risk_low is not None:
        risk_status = "HIGH RISK" if predicted_risk_low == 1 else "LOW RISK"
        log(f"Predicted Risk Status: {risk_status}")

    log("\n==== Risk Prediction Script Completed ====")
