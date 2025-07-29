# utils.py

import spacy
from config import TECH_KEYWORDS

# Load spaCy NER model
nlp = spacy.load("en_core_web_sm")

def extract_named_entities(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents]

def contains_tech_keywords(text):
    text_lower = text.lower()
    return [kw for kw in TECH_KEYWORDS if kw.lower() in text_lower]
