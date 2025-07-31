from .schema_setup import setup_constraints
from .operations import (
    add_trapper,
    add_victim,
    connect_trapper_to_victim,
    add_red_team_report,
    link_threat_type,
    link_target_group
)

def insert_batch_scenario():
    # Create trapper
    trapper_id = add_trapper("BlackWidow", "widow_hunterx", "Instagram")

    # Add 5 army officer victims
    for i in range(1, 6):
        victim_name = f"army_officer_{i}"
        victim_id = add_victim(victim_name, "Instagram")
        connect_trapper_to_victim(trapper_id, victim_id)

    # Add red team report
    add_red_team_report(
        trapper_id,
        "Sent malicious links disguised as defense job offers.",
        "High"
    )

    # Classify as phishing
    link_threat_type(trapper_id, "Phishing")

    # Tag target group
    link_target_group(trapper_id, "Defense Personnel")

    print("✅ Scenario inserted: 1 trapper → 5 army officers (phishing).")
if __name__ == "__main__":
    setup_constraints()
    insert_batch_scenario()
