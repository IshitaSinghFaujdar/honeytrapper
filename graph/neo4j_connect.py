from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
 # Replace with your actual credentials
load_dotenv()
URI = os.getenv("URI")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
AUTH = (USER, PASSWORD)

def test_connection():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    try:
        driver.verify_connectivity()
        print("✅ Connected to Neo4j successfully!")
    except Exception as e:
        print("❌ Connection failed:", e)
    finally:
        driver.close()

if __name__ == "__main__":
    test_connection()
