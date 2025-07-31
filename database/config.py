import os
from dotenv import load_dotenv

# Load .env from one level above the database directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

NEO4J_URI = os.getenv("URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
