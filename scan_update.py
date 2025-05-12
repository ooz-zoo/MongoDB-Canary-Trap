import os
import random
import requests
from pymongo import MongoClient
from multiprocessing import Process, Pipe
from datetime import datetime

# mongo setup
atlas_connection_string = os.getenv("ENV_DB")
mongo_client = MongoClient(atlas_connection_string)
db = mongo_client["backup_archives"]

collections = ["credentials", "database_dump", "employee_salaries"]
batch_size = 2

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").text 
    except:
        return "UNKNOWN_IP"

# child process
def update_last_accessed(conn):
    while True:
        doc_id = conn.recv()  # Wait for parent to send a document ID
        if doc_id == "EXIT":
            break
        
        # Update MongoDB
        db[doc_id["collection"]].update_one(
            {"_id": doc_id["_id"]},
            {"$set": {"last_accessed": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
        )
        print(f"Child updated last_accessed: {doc_id}")

# parent process-scans documents
def attacker_scan():
    parent_conn, child_conn = Pipe()  # Create a pipe for communication
    child = Process(target=update_last_accessed, args=(child_conn,))
    child.start()  # Launch child process

    print("Starting ransomware simulation scan")
    print("\n[!] SIMULATED ATTACKER IP:", get_public_ip(), "\n")
    
    for collection_name in collections:
        collection = db[collection_name]
        total_records = collection.count_documents({})
        print(f"Scanning collection: {collection_name} (Total records: {total_records})")

        for i in range(0, total_records, batch_size):
            documents = collection.find().skip(i).limit(batch_size)
            for doc in documents:
                # Simulate scan metrics
                scanned_info = {
                    "collection": collection_name,
                    "_id": doc["_id"],
                    "size_kb": round(len(str(doc)) / 1024, 2),
                }
                print(f"Scanned document: {scanned_info}")

                # Send doc ID to child for last_accessed update
                parent_conn.send({
                    "collection": collection_name,
                    "_id": doc["_id"]
                })

    parent_conn.send("EXIT")  # Tell child to exit
    child.join()  # Wait for child to finish
    print("Scan completed")

if __name__ == "__main__":
    attacker_scan()
