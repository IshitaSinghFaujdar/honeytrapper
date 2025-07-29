import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

# Load original training data
df = pd.read_csv("D:/honeytrap/simulated_instagram_profiles.csv")

# Recreate and fit vectorizer
vectorizer = TfidfVectorizer(max_features=300)
vectorizer.fit(df['bio'])

# Save vectorizer
joblib.dump(vectorizer, "D:/honeytrap/tfidf_vectorizer.pkl")
