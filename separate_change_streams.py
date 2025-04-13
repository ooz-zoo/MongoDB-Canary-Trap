import os
import pymongo
import requests
from datetime import datetime

# Shared resource for alerts
shared_alerts = []

def get_attacker_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "Unknown IP"  

# MongoDB Change Stream
db = pymongo.MongoClient(os.environ['ENV_DB'])
change_stream = db.watch([{
    '$match': {
        'operationType': 'update',
        'updateDescription.updatedFields.last_accessed': {'$exists': True}
    }
}])

print("[!] Listening for database changes (last_accessed updates)...")

for change in change_stream:
    collection_name = change["ns"]["coll"]
    doc_id = change["documentKey"]["_id"]
    timestamp = change["updateDescription"]["updatedFields"]["last_accessed"]
    attacker_ip = get_attacker_ip()  

    # Prepare alert data
    alert = {
        "time": datetime.now(),
        "ip": attacker_ip,
        "collection": collection_name,
        "doc_id": str(doc_id),
        "last_accessed": str(timestamp)
    }

    # Push alert to shared resource
    shared_alerts.append(alert)

    # Print alert to console
    print(f"""
    \033[91m[ALERT] DB scans detected!\033[0m 
    - Collection: {collection_name}
    - Attacker IP: {attacker_ip}
    - Document ID: {doc_id}
    - Last Accessed: {timestamp}
    """)
