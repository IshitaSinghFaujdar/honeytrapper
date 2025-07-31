from .driver import driver

def setup_constraints():
    with driver.session() as session:
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:ThreatType) REQUIRE t.type IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (g:TargetGroup) REQUIRE g.name IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (i:Incident) REQUIRE i.incident_id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:RedTeamReport) REQUIRE r.report_id IS UNIQUE")
