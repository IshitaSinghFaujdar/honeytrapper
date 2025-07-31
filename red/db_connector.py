# --- db_connector.py ---

from neo4j import GraphDatabase
import streamlit as st
import logging

log = logging.getLogger(__name__)

class Neo4jConnection:
    
    def __init__(self, uri, user, password):
        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verify that the connection is valid
            self._driver.verify_connectivity()
            log.info("Successfully connected to Neo4j Aura.")
        except Exception as e:
            log.error(f"Failed to create Neo4j driver: {e}")
            self._driver = None

    def close(self):
        if self._driver is not None:
            self._driver.close()

    def submit_report(self, user_session_id, profile_data, chat_analysis, final_verdict):
        """
        Submits a full analysis report to the Neo4j database.
        Creates nodes and relationships based on our data model.
        """
        if self._driver is None:
            log.error("Cannot submit report, Neo4j driver not available.")
            return False
            
        with self._driver.session(database="neo4j") as session:
            try:
                # Use a single transaction to ensure all or nothing is written
                session.execute_write(self._create_report_tx, user_session_id, profile_data, chat_analysis, final_verdict)
                log.info(f"Successfully submitted report for scammer: {profile_data['username']}")
                return True
            except Exception as e:
                log.error(f"Failed to write report to Neo4j: {e}", exc_info=True)
                return False

    @staticmethod
    def _create_report_tx(tx, user_session_id, profile, analysis, final_verdict):
        # 1. Create or Merge the User node (the person reporting)
        tx.run("MERGE (u:User {id: $session_id})", session_id=user_session_id)

        # 2. Create or Merge the Scammer node
        scammer_query = """
        MERGE (s:Scammer {username: $username})
        ON CREATE SET 
            s.followers = $followers, s.following = $following, s.bio = $bio, 
            s.is_private = $is_private, s.is_verified = $is_verified, 
            s.report_count = 1, s.first_reported_on = timestamp(), s.last_reported_on = timestamp()
        ON MATCH SET 
            s.followers = $followers, s.following = $following, s.bio = $bio, 
            s.is_private = $is_private, s.is_verified = $is_verified, 
            s.report_count = s.report_count + 1, s.last_reported_on = timestamp()
        """
        tx.run(scammer_query, 
               username=profile['username'], followers=profile.get('followers'),
               following=profile.get('following'), bio=profile.get('bio'),
               is_private=profile.get('is_private'), is_verified=profile.get('is_verified'))

        # 3. Create the REPORTED relationship
        tx.run("""
        MATCH (u:User {id: $session_id})
        MATCH (s:Scammer {username: $username})
        MERGE (u)-[r:REPORTED {timestamp: timestamp()}]->(s)
        SET r.final_verdict_score = $score
        """, session_id=user_session_id, username=profile['username'], score=final_verdict)

        # 4. Create Tactic nodes and relationships
        psych_analysis = analysis.get('psychological_analysis', {})
        for tactic, details in psych_analysis.items():
            if tactic != 'total_risk_score' and details.get('score', 0) > 0:
                tx.run("""
                MATCH (s:Scammer {username: $username})
                MERGE (t:Tactic {name: $tactic_name})
                MERGE (s)-[:USED_TACTIC]->(t)
                """, username=profile['username'], tactic_name=tactic)

# A helper function to easily get a connection instance
# @st.cache_resource is a decorator that tells Streamlit to run this function only once
# and cache the result. This prevents creating a new database connection on every rerun.
@st.cache_resource
def get_db_connection():
    """Gets a cached Neo4j connection using Streamlit secrets."""
    log.info("Attempting to get DB connection...")
    try:
        uri = st.secrets["NEO4J_URI"]
        user = st.secrets["NEO4J_USERNAME"]
        password = st.secrets["NEO4J_PASSWORD"]
        return Neo4jConnection(uri, user, password)
    except KeyError as e:
        # This error is helpful if you forget a key in your secrets.toml file
        st.error(f"Neo4j credential '{e.args[0]}' not found in secrets.toml. Please add it.")
        log.error(f"Neo4j credential '{e.args[0]}' not found in secrets.toml.")
        return None