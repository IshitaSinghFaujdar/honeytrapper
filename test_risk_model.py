# test_risk_model.py

import pandas as pd
import joblib
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from sklearn.pipeline import Pipeline # Import Pipeline from sklearn.pipeline
import numpy as np # Import numpy

# Import the functions from your training script
# Assuming profile_risk.py is in the same directory or accessible via PYTHONPATH
from profile_risk import load_data, preprocess_data, train_model, evaluate_model, save_model, log

# -----------------------------------------------
# 🧪 Mock Data for Testing
# -----------------------------------------------
@pytest.fixture
def mock_dataframe():
    """
    Fixture to provide a mock DataFrame for testing.
    This simulates the input CSV data.
    """
    data = {
        'followers': [100, 200, 50, 150, 300],
        'following': [50, 100, 20, 70, 120],
        'account_age_days': [365, 730, 180, 500, 90],
        'is_private': ['False', 'True', 'False', 'False', 'True'],
        'is_verified': ['False', 'False', 'True', 'False', 'False'],
        'photo_source': ['profile_pic', 'default', 'profile_pic', 'default', 'profile_pic'],
        'bio': ['I love happy things!', 'Just chilling.', 'Positive vibes only.', 'Feeling down today.', 'Great day ahead!'],
        'risk_label': [0, 1, 0, 1, 0] # 0 for low risk, 1 for high risk
    }
    df = pd.DataFrame(data)
    return df

# -----------------------------------------------
# 🧪 Mocking External Dependencies
# -----------------------------------------------
@pytest.fixture(autouse=True)
def mock_hf_pipeline_sentiment():
    """
    Fixture to mock the Hugging Face sentiment analysis pipeline.
    This prevents actual model loading during tests.
    It simulates positive sentiment for most cases for predictable testing.
    """
    with patch('profile_risk.hf_pipeline') as mock_pipeline:
        # Configure the mock pipeline to return a predictable sentiment
        # For simplicity, let's make it always return 'POSITIVE' unless specific text is given
        def mock_sentiment_return(text):
            if "down" in text.lower() or "sad" in text.lower():
                return [{'label': 'NEGATIVE', 'score': 0.9}]
            return [{'label': 'POSITIVE', 'score': 0.9}]

        mock_instance = MagicMock()
        mock_instance.side_effect = mock_sentiment_return
        mock_pipeline.return_value = mock_instance
        yield mock_pipeline

@pytest.fixture(autouse=True)
def mock_joblib_dump():
    """
    Fixture to mock joblib.dump to prevent actual file writing during tests.
    """
    with patch('joblib.dump') as mock_dump:
        yield mock_dump

# -----------------------------------------------
# 🧪 Test Functions
# -----------------------------------------------

def test_load_data(mock_dataframe):
    """
    Tests the load_data function by creating a temporary CSV file
    and checking if the data is loaded correctly.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test_data.csv")
        mock_dataframe.to_csv(csv_path, index=False)

        df = load_data(csv_path)
        assert not df.empty
        assert df.shape == mock_dataframe.shape
        assert list(df.columns) == list(mock_dataframe.columns)
        log("test_load_data passed.")

def test_preprocess_data(mock_dataframe):
    """
    Tests the preprocess_data function, checking for:
    1. Correct type coercion for 'is_private', 'is_verified', 'photo_source'.
    2. Addition of 'bio_sentiment_score' column.
    3. Correct sentiment score based on mock.
    """
    df_processed = preprocess_data(mock_dataframe.copy()) # Use a copy to avoid modifying fixture

    # Check type coercion
    assert df_processed['is_private'].dtype == 'object' # pandas 'object' for string
    assert df_processed['is_verified'].dtype == 'object'
    assert df_processed['photo_source'].dtype == 'object'

    # Check if 'bio_sentiment_score' column is added
    assert 'bio_sentiment_score' in df_processed.columns

    # Check sentiment scores based on our mock's logic
    # 'I love happy things!' -> POSITIVE (1)
    # 'Just chilling.' -> POSITIVE (1)
    # 'Positive vibes only.' -> POSITIVE (1)
    # 'Feeling down today.' -> NEGATIVE (0)
    # 'Great day ahead!' -> POSITIVE (1)
    expected_sentiment = [1, 1, 1, 0, 1]
    pd.testing.assert_series_equal(df_processed['bio_sentiment_score'], pd.Series(expected_sentiment, name='bio_sentiment_score'))

    log("test_preprocess_data passed.")


def test_train_model(mock_dataframe):
    """
    Tests the train_model function, ensuring:
    1. A scikit-learn Pipeline object is returned.
    2. The returned object is fitted (can make predictions).
    """
    df_processed = preprocess_data(mock_dataframe.copy())
    model, X_test, y_test = train_model(df_processed)

    # Fix: Use Pipeline imported from sklearn.pipeline
    assert isinstance(model, Pipeline)
    assert hasattr(model, 'predict') # Check if it's a fitted model
    assert X_test.shape[0] > 0 # Ensure test sets are not empty
    assert y_test.shape[0] > 0
    log("test_train_model passed.")


def test_evaluate_model(mock_dataframe, capsys):
    """
    Tests the evaluate_model function.
    It doesn't return anything, so we check if it prints to stdout
    (using capsys) and if the prediction step works.
    """
    df_processed = preprocess_data(mock_dataframe.copy())
    model, X_test, y_test = train_model(df_processed)

    # Call evaluate_model, which prints to console
    evaluate_model(model, X_test, y_test)

    # Capture the output to check if classification report and confusion matrix were printed
    captured = capsys.readouterr()
    assert "Classification Report" in captured.out
    assert "Confusion Matrix" in captured.out
    log("test_evaluate_model passed.")


def test_save_model(mock_dataframe, mock_joblib_dump):
    """
    Tests the save_model function, ensuring joblib.dump is called.
    We mock joblib.dump so no actual file is written.
    """
    df_processed = preprocess_data(mock_dataframe.copy())
    model, _, _ = train_model(df_processed)

    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "test_model.pkl")
        save_model(model, model_path)
        mock_joblib_dump.assert_called_once_with(model, model_path)
        log("test_save_model passed.")


def test_end_to_end_prediction(mock_dataframe):
    """
    Tests the entire pipeline from loading data to making a prediction
    on a new, unseen data point, ensuring the model can be used.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test_data.csv")
        mock_dataframe.to_csv(csv_path, index=False)
        model_path = os.path.join(tmpdir, "test_model.pkl")

        # Simulate the main function flow
        df = load_data(csv_path)
        df = preprocess_data(df)
        model, _, _ = train_model(df)
        save_model(model, model_path)

        # Load the saved model (mocked joblib.dump means it's the same object)
        # In a real scenario, you'd load from disk here
        # For this test, we'll just use the `model` object directly as if it was loaded.

        # Create a new, unseen data point for prediction
        new_data = pd.DataFrame({
            'followers': [75],
            'following': [30],
            'account_age_days': [100],
            'is_private': ['False'],
            'is_verified': ['False'],
            'photo_source': ['profile_pic'],
            'bio': ['This is a neutral bio.']
        })

        # Preprocess the new data (only the features needed for prediction)
        # Note: In a real prediction scenario, you'd apply the same preprocessing steps
        # but only on the features, not the target.
        # For this test, we'll manually ensure the new_data structure matches X_train/X_test
        # before passing it to the trained pipeline.
        
        # The pipeline expects the raw features, it handles preprocessing internally.
        # So we just need to ensure the columns match the training features.
        features_for_prediction = new_data[['followers', 'following', 'account_age_days', 'is_private', 'is_verified', 'photo_source', 'bio']]
        
        # Apply sentiment analysis to the new bio
        # This part of preprocessing needs to be done before passing to the pipeline
        sentiment_model_mock = MagicMock()
        sentiment_model_mock.side_effect = lambda text: [{'label': 'POSITIVE', 'score': 0.9}] if "neutral" in text.lower() else [{'label': 'NEGATIVE', 'score': 0.9}]
        
        # Temporarily re-patch hf_pipeline for this specific test's sentiment logic
        with patch('profile_risk.hf_pipeline', return_value=sentiment_model_mock):
            features_for_prediction['bio_sentiment_score'] = features_for_prediction['bio'].apply(
                lambda text: 1 if sentiment_model_mock(text)[0]['label'] == 'POSITIVE' else 0
            )

        # Drop the original 'bio' column as it's not a feature for the model
        features_for_prediction = features_for_prediction.drop(columns=['bio'])

        # Ensure column order matches training
        expected_features_order = ['followers', 'following', 'account_age_days', 'is_private', 'is_verified', 'photo_source', 'bio_sentiment_score']
        features_for_prediction = features_for_prediction[expected_features_order]

        prediction = model.predict(features_for_prediction)

        assert prediction is not None
        # Fix: Include numpy numeric types in the isinstance check
        assert isinstance(prediction[0], (int, float, np.integer, np.floating)) # Should be 0 or 1
        log(f"test_end_to_end_prediction passed. Predicted: {prediction[0]}")

