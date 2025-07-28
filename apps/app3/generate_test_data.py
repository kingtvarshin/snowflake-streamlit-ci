import pandas as pd
import numpy as np
import random
import datetime
import json

N = 100

custodian_teams = ["Network", "Database", "Application", "Security", "DevOps", "Support"]
failure_categories = ["Hardware", "Software", "Security", "Network", "Database"]
failure_sub_categories = {
    "Hardware": ["Router", "Switch", "Server", "Disk"],
    "Software": ["API Outage", "Database Crash", "Firmware", "Service Down"],
    "Security": ["Unauthorized Access", "Phishing", "Malware", "DDoS"],
    "Network": ["Latency", "Packet Loss", "Link Down"],
    "Database": ["Corruption", "Slow Query", "Crash"]
}
failure_caused_by_list = ["Power Surge", "Bug", "Human Error", "Out of Memory", "Compromised Credentials", "Deployment Error", "Phishing Attack", "Network Issue"]
failure_reasons = ["Overvoltage", "Memory Leak", "High query load", "Misconfigured env", "Phishing", "Firmware Bug", "Network Congestion", "Disk Full"]
action_taken = ["Replaced Router", "Restarted Database", "Rolled Back Deployment", "Reset Credentials", "Patched Firmware", "Blocked Access", "Scaled Resources", "Restored Backup"]
action_category = ["Replacement", "Recovery", "Rollback", "Mitigation", "Patch", "Scale", "Restore"]
prior_notification = ["Yes", "No"]
comments_samples = [
    "Incident resolved after action.",
    "PagerDuty alert acknowledged.",
    "Stakeholders notified.",
    "Root cause analysis scheduled.",
    "Credentials reset and access blocked.",
    "Deployment rolled back successfully.",
    "Database restored from backup.",
    "Firmware patched and tested."
]
users = ["alice", "bob", "carol", "dave", "eve", "frank", "grace", "heidi"]

def random_datetime(start, end):
    """Generate a random datetime between start and end"""
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )

start_date = datetime.datetime(2021, 1, 1)
end_date = datetime.datetime(2025, 7, 28)

data = []
for i in range(1, N+1):
    fc = random.choice(failure_categories)
    fsc = random.choice(failure_sub_categories[fc])
    incident_id = i
    incident_number = f"INC{1000+i}"
    custodian_team = random.choice(custodian_teams)
    failure_category = fc
    failure_sub_category = fsc
    failure_caused_by = random.choice(failure_caused_by_list)
    failure_reason = random.choice(failure_reasons)
    action_taken_val = random.choice(action_taken)
    action_category_val = random.choice(action_category)
    actual_time_spent = round(random.uniform(10, 120), 2) if random.random() > 0.05 else None
    parent_incident_number = f"INC{random.randint(1001, 1000+N)}" if random.random() < 0.1 else ""
    prior_notification_val = random.choice(prior_notification)
    created_on = random_datetime(start_date, end_date)
    updated_on = (created_on + datetime.timedelta(minutes=random.randint(1, 120))).isoformat()
    created_on = (created_on).isoformat()
    created_by = random.choice(users)
    updated_by = random.choice(users)
    comments = random.choice(comments_samples) if random.random() > 0.1 else ""

    # --- Tagged/untagged logic ---
    # About half tagged, half untagged
    if random.random() < 0.9:
        # Tagged: at least one field is filled
        tagged = True
    else:
        # Untagged: most fields are empty or None
        custodian_team = ""
        failure_category = ""
        failure_sub_category = ""
        failure_caused_by = ""
        failure_reason = ""
        action_taken_val = ""
        action_category_val = ""
        actual_time_spent = None
        parent_incident_number = ""
        prior_notification_val = ""
        created_by = ""
        updated_by = ""
        comments = ""
        tagged = False
        created_on = None
        updated_on = None

    data.append({
        "incident_id": incident_id,
        "incident_number": incident_number,
        "custodian_team": custodian_team,
        "failure_category": failure_category,
        "failure_sub_category": failure_sub_category,
        "failure_caused_by": failure_caused_by,
        "failure_reason": failure_reason,
        "action_taken": action_taken_val,
        "action_category": action_category_val,
        "actual_time_spent_in_minutes": actual_time_spent,
        "parent_incident_number": parent_incident_number,
        "prior_notification": prior_notification_val,
        "record_created_on": created_on,
        "record_created_by": created_by,
        "record_updated_on": updated_on,
        "record_updated_by": updated_by,
        "comments": comments,
        "tagged": tagged
    })

with open("d:/Github/snowflake-streamlit-ci/apps/app3/data.json", "w") as f:
    json.dump(data, f, indent=2)