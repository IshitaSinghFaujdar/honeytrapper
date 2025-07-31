# operations.py (FULLY CORRECTED AND VERIFIED VERSION)

from .driver import driver
import uuid

# -----------------------------
# Helper: Generate UUID
# -----------------------------
def generate_id():
    return str(uuid.uuid4())

# -----------------------------
# Add a trapper node
# -----------------------------
def add_trapper(trapper_id, platform, username):
    with driver.session() as session:
        session.run(
            """
            MERGE (t:Trapper {id: $id})
            ON CREATE SET t.username = $username,
                          t.platform = $platform
            """,
            id=trapper_id, username=username, platform=platform
        )
    return trapper_id

# -----------------------------
# Add a victim node
# -----------------------------
def add_victim(victim_id, platform):
    with driver.session() as session:
        session.run(
            """
            MERGE (v:Victim {id: $id})
            ON CREATE SET v.platform = $platform
            """,
            id=victim_id, platform=platform
        )
    return victim_id

#--------------
# Log victim metadata
#--------------
def log_victim_metadata(victim_id, age_group, gender, location, platform, profession):
    with driver.session() as session:
        session.run(
            """
            MATCH (v:Victim {id: $victim_id})
            SET v.age_group = $age_group,
                v.gender = $gender,
                v.location = $location,
                v.platform = $platform,
                v.profession = $profession
            """,
            {
                "victim_id": victim_id,
                "age_group": age_group,
                "gender": gender,
                "location": location,
                "platform": platform,
                "profession": profession
            }
        )

# -----------------------------
# Connect trapper to victim
# -----------------------------
def connect_trapper_to_victim(trapper_id, victim_id):
    with driver.session() as session:
        session.run(
            """
            MATCH (t:Trapper {id: $trapper_id})
            MATCH (v:Victim {id: $victim_id})
            MERGE (t)-[:TARGETED]->(v)
            """,
            trapper_id=trapper_id, victim_id=victim_id
        )

# -----------------------------
# Add Red Team Report
# -----------------------------
def add_red_team_report(report_id, victim_id, severity):
    with driver.session() as session:
        session.run(
            """
            MATCH (v:Victim {id: $victim_id})
            MERGE (r:RedTeamReport {id: $report_id})
            SET r.severity = $severity,
                r.timestamp = datetime()
            MERGE (v)-[:SUBJECT_OF]->(r)
            """,
            victim_id=victim_id,
            report_id=report_id,
            severity=severity
        )
    return report_id

# -----------------------------
# Link Trapper to Threat Type
# -----------------------------
def link_threat_type(trapper_id, threat_type):
    with driver.session() as session:
        session.run(
            """
            MATCH (t:Trapper {id: $trapper_id})
            MERGE (threat:ThreatType {name: $threat_type})
            MERGE (t)-[:CLASSIFIED_AS]->(threat)
            """,
            trapper_id=trapper_id, threat_type=threat_type
        )

# -----------------------------
# Link Trapper to Target Group
# -----------------------------
def link_target_group(trapper_id, group_name):
    with driver.session() as session:
        session.run(
            """
            MATCH (t:Trapper {id: $trapper_id})
            MERGE (g:TargetGroup {name: $group_name})
            MERGE (t)-[:TARGETS_GROUP]->(g)
            """,
            trapper_id=trapper_id, group_name=group_name
        )

# -----------------------------
# The function that caused the error - NOW FIXED
# -----------------------------
def create_threat_type(tx, report_id, trapper_id, threat_name, confidence):
    # This query is restructured to do all MATCHing first, which resolves the syntax error.
    # It also uses the correct property key 'id' to find the nodes.
    tx.run("""
        MATCH (r:RedTeamReport {id: $report_id})
        MATCH (t:Trapper {id: $trapper_id})
        MERGE (tt:ThreatType {type: $threat_name})
        ON CREATE SET tt.confidence = $confidence
        ON MATCH SET tt.confidence = $confidence
        MERGE (r)-[:DETECTED]->(tt)
        MERGE (t)-[:CLASSIFIED_AS]->(tt)
    """,
    threat_name=threat_name,
    confidence=confidence,
    report_id=report_id,
    trapper_id=trapper_id)

def add_threat_type(report_id, trapper_id, threat_name, confidence):
    with driver.session() as session:
        session.write_transaction(create_threat_type, report_id, trapper_id, threat_name, confidence)