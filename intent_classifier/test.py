# test.py

import unittest
import os
import numpy as np

# --- Important: Make sure the model is trained before running tests ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "intent_classifier_model.pkl")
MODEL_EXISTS = os.path.exists(MODEL_PATH)

# --- Import the functions we want to test ---
# We use a try/except block to give a helpful error if a file is missing
try:
    from utils import contains_tech_keywords, extract_named_entities
    from model import embed_text, predict_intent
    from classify import classify_message_window
except ImportError as e:
    print(f"Error: Could not import a required module. Make sure all files (utils.py, model.py, classify.py) exist. Details: {e}")
    exit()


class TestUtils(unittest.TestCase):
    """Tests for helper functions in utils.py"""

    def test_contains_tech_keywords_positive(self):
        """Should find keywords present in the text."""
        text = "Can I get access to the github repo?"
        # Note: assumes keywords in config.py are lowercase
        expected = ["access", "github", "repo"]
        self.assertEqual(sorted(contains_tech_keywords(text.lower())), sorted(expected))

    def test_contains_tech_keywords_negative(self):
        """Should return an empty list if no keywords are found."""
        text = "How was your day? The weather is nice."
        self.assertEqual(contains_tech_keywords(text), [])

    def test_extract_named_entities(self):
        """Should correctly extract names and organizations."""
        text = "My name is Alice and I work at Google."
        entities = extract_named_entities(text)
        self.assertIn("Alice", entities)
        self.assertIn("Google", entities)


@unittest.skipIf(not MODEL_EXISTS, "Skipping model tests because 'intent_classifier_model.pkl' not found. Run train.py first.")
class TestModel(unittest.TestCase):
    """Tests for the machine learning model functions in model.py"""

    def test_embed_text_output(self):
        """Should return a numpy array of a specific shape."""
        embedding = embed_text("This is a test sentence.")
        self.assertIsInstance(embedding, np.ndarray)
        # The 'all-MiniLM-L6-v2' model produces embeddings of size 384
        self.assertEqual(embedding.shape, (1, 384))

    def test_predict_intent_return_types(self):
        """Should return a boolean and a float."""
        prediction, confidence = predict_intent("some random text")
        self.assertIsInstance(prediction, (bool, np.bool_))
        self.assertIsInstance(confidence, (float, np.float64))

    def test_predict_intent_on_anomalous_text(self):
        """Should predict True for a clearly anomalous message."""
        prediction, _ = predict_intent("what is the database password?")
        self.assertTrue(prediction)

    def test_predict_intent_on_benign_text(self):
        """Should predict False for a clearly benign message."""
        prediction, _ = predict_intent("I like chatting with you!")
        self.assertFalse(prediction)


@unittest.skipIf(not MODEL_EXISTS, "Skipping classifier tests because 'intent_classifier_model.pkl' not found. Run train.py first.")
class TestClassifier(unittest.TestCase):
    """Integration test for the main classification function in classify.py"""

    def test_classify_message_window_anomalous(self):
        """Should produce an 'anomalous' result dictionary."""
        messages = ["can you access the production server?"]
        result = classify_message_window(messages)
        self.assertEqual(result["intent"], "anomalous")
        self.assertTrue(result["anomaly"]) # Check the final boolean flag
        self.assertIn("server", result["keywords"])

    def test_classify_message_window_benign(self):
        """Should produce a 'benign' result dictionary."""
        messages = ["you have beautiful eyes", "let's meet up sometime"]
        result = classify_message_window(messages)
        self.assertEqual(result["intent"], "benign")
        self.assertFalse(result["anomaly"]) # Check the final boolean flag


# This allows the script to be run from the command line
if __name__ == '__main__':
    print("Running unit tests...")
    unittest.main()