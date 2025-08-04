'''
as per your assigned SET of file 
process the file and write the python code to 
    -- 1. identify to which base resource it belongs to
    -- 2. error log the duplicate and validation error entries 
    -- 3. convert the valid records to fhir bundle as POST request 
    -- 4. ingest the bundle to hapi server.
'''

import csv
import json
import os
import sys
from collections import defaultdict
import requests

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Config import (you must create this config.py with values)
from config import (
    FHIR_BASE_HAPI_URL,
    HEADERS,
    INPUT_CSV,
    OUTPUT_BUNDLE,
    ERROR_LOG,
    LEARNER_NAME
)

# Fields required for basic Location resource
REQUIRED_FIELDS = ["id", "name", "status", "address_line", "address_state"]

def is_valid_row(row):
    """Check if all required fields are present and non-empty."""
    return all(row.get(field) for field in REQUIRED_FIELDS)

def convert_to_location_resource(resource_id, grouped_rows):
    """Convert grouped CSV rows into one Location FHIR resource."""
    base = grouped_rows[0]
    hours = []

    for row in grouped_rows:
        if row.get("hours_of_operation_days_of_week"):
            try:
                hours.append({
                    "daysOfWeek": [row["hours_of_operation_days_of_week"]],
                    "allDay": row["hours_of_operation_all_day"].strip().lower() == 'true'
                })
            except:
                pass

    location = {
        "resourceType": "Location",
        "id": resource_id,
        "name": base["name"],
        "status": base["status"],
        "address": {
            "line": [base["address_line"]],
            "state": base["address_state"]
        },
        "meta": {
            "tag": [{
                "code": f"Learners-{LEARNER_NAME}",
                "display": "Learners-FHIR-Assessment"
            }]
        }
    }

    # Add hours of operation if present
    if hours:
        location["hoursOfOperation"] = hours

    # Add coordinates if valid
    if base.get("position_longitude") and base.get("position_latitude"):
        try:
            location["position"] = {
                "longitude": float(base["position_longitude"]),
                "latitude": float(base["position_latitude"])
            }
        except ValueError:
            pass

    return location

def build_fhir_bundle(entries):
    """Wrap entries into a FHIR batch bundle."""
    return {
        "resourceType": "Bundle",
        "type": "batch",
        "entry": entries
    }

def main():
    seen_row_keys = set()
    bundle_entries = []
    error_entries = []
    grouped_data = defaultdict(list)

    # Make sure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_BUNDLE), exist_ok=True)

    # Step 1: Read CSV and group valid rows by resource ID
    with open(INPUT_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row_key = (row.get("id"), row.get("hours_of_operation_days_of_week"), row.get("hours_of_operation_all_day"))

            if row_key in seen_row_keys:
                row["error"] = "Duplicate day/hour entry for resource"
                error_entries.append(row)
                continue

            if not is_valid_row(row):
                row["error"] = "Missing required fields"
                error_entries.append(row)
                continue

            seen_row_keys.add(row_key)
            grouped_data[row["id"]].append(row)

    # Step 2: Convert valid groups to Location resources
    for resource_id, rows in grouped_data.items():
        location_resource = convert_to_location_resource(resource_id, rows)
        bundle_entries.append({
            "request": {"method": "POST", "url": "Location"},
            "resource": location_resource
        })

    # Step 3: Save bundle to JSON file
    bundle = build_fhir_bundle(bundle_entries)
    with open(OUTPUT_BUNDLE, "w") as f:
        json.dump(bundle, f, indent=2)

    # Step 4: Write error log
    if error_entries:
        with open(ERROR_LOG, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=error_entries[0].keys())
            writer.writeheader()
            writer.writerows(error_entries)

    print(f"\nBundle created with {len(bundle_entries)} valid Location resources.")
    print(f"{len(error_entries)} error entries logged.")

    # Step 5: POST to FHIR server
    try:
        response = requests.post(FHIR_BASE_HAPI_URL, headers=HEADERS, json=bundle)
        if response.status_code in (200, 201):
            print("Bundle successfully ingested into HAPI FHIR server.")
        else:
            print(f"Failed to upload bundle. Status: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print("Exception during POST to FHIR server:", str(e))

if __name__ == "__main__":
    main()