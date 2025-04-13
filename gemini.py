import os
from pymongo import MongoClient
from google import genai
import json
import re

api_key= os.getenv("API_KEY")

client = genai.Client(api_key=api_key)

# Define the request for generating decoy data
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=(
        "Generate realistic-looking decoy data for the following three files in JSON format. "
        "Each file should have at least 3 records and mimic real-world data with appropriate fields. "
        "The data should be believable to an attacker but not use real data. "
        "Include realistic timestamps (e.g., creation_date, last_accessed, and last_modified) where applicable. "
        "Here are the file details:\n\n"
        "1. credentials.json: Contains fields like 'username', 'password', 'email', 'creation_date', 'last_modified', and 'last_accessed'.\n"
        "2. employee_salaries.xlsx: Contains fields like 'employee_id', 'name', 'position', 'salary', 'creation_date', 'last_modified', and 'last_accessed'.\n"
        "3. database_dump.sql: Mimic a SQL dump with fields like 'id', 'table_name', 'query', 'creation_date', 'last_modified', and 'last_accessed'.\n\n"
        "For all records across all files, set the last_accessed field to null. "
        "Ensure passwords are hashed. "
        "Make sure nothing in the data hints at being a honeypot; it must look real. "
        "Use ISO format for timestamps in the creation_date and last_modified fields. "
        "THE DATABASE_DUMP.SQL FILE THE QUERIES SHOULD BE VARIED DONT JUST HAVE INSERT COME ON AND HAVE SOMEHTING INTERESTING IN THERE THAT WILL ATTRACT AN ATTACKER"
        "JUST GIVE ME THE DATA DONT COMMENT OR ANYTHING"
        "REMEMBER JUST THREE RECORDS PER FILE ONLY"
        "DONT USE ANYTHING LIKE EXAMPLE ANYWHERE IT MAKES IT LOOK LIKE A HONEYPOT TO THE ATTACKER"
        "Ensure the data is structured and formatted correctly for each file type."
    )
)

# Parse gemini response
input_text=response.text

#regex to extract JSON from response
json_blocks = re.findall(r'```json\n(.*?)\n```', input_text, re.DOTALL)

# Parse each JSON block and combine them into one list
generated_data = []
for block in json_blocks:
    try:
        data = json.loads(block.strip()) # remove newlines from JSON text and convert json string to a py list
        if isinstance(data, list):
            generated_data.extend(data)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON block: {e}")

# connection string 
atlas_environ = os.getenv("ENV_DB")

# connect to atlas
mongo_client = MongoClient(atlas_environ)
db = mongo_client["backup_archives"]

#insert data
try:
    # Categorize records based on unique fields
    credentials = []
    employee_payrolls = []
    database_dump = []

    for record in generated_data:
        if "username" in record and "password" in record:  # Likely a credential record
            credentials.append(record)
        elif "employee_id" in record and "salary" in record:  # Likely an employee salary record
            employee_payrolls.append(record)
        elif "table_name" in record and "query" in record:  # Likely a database dump record
            database_dump.append(record)

    # Insert categorized data into respective MongoDB collections
    if credentials:
        db.credentials.insert_many(credentials)
        print(f"Inserted {len(credentials)} records into the 'credentials' collection.")

    if employee_payrolls:
        db.employee_salaries.insert_many(employee_payrolls)
        print(f"Inserted {len(employee_payrolls)} records into the 'employee_salaries' collection.")

    if database_dump:
        db.database_dump.insert_many(database_dump)
        print(f"Inserted {len(database_dump)} records into the 'database_dump' collection.")

    print("All data successfully categorized and inserted into MongoDB Atlas!")

except Exception as e:
    print(f"An error occurred: {e}")