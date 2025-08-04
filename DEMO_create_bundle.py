"""
create_bundle.py

This script processes a CSV file, 
identifies the FHIR resource type, 
validates the data, removes duplicates, logs errors, 
generates a FHIR Bundle (batch) with POST entries,
and ingests them to a FHIR server (e.g., HAPI server).
"""

import csv
import json
import os
import sys
from collections import defaultdict

import requests

# Add root directory to Python path for importing config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import constants from config
from config import FHIR_BASE_HAPI_URL, HEADERS, INPUT_CSV, OUTPUT_BUNDLE, ERROR_LOG,LEARNER_NAME

def is_valid_row(row):
    required_fields = ["identifier", "name", "gender", "birthDate"]
    return all(row.get(field) for field in required_fields)

def convert_to_patient_resource(row):
    return {
        "meta": {
            "tag": [
                {
                    "code": f"Learners-{LEARNER_NAME}",
                    "display": "Learners-FHIR-Assessment"
                }
            ]
        },
        "resourceType": "Patient",
        "identifier": [{
            "system": "http://hospital.smarthealth.org/patient-ids",
            "value": row["identifier"]
        }],
        "name": [{"text": row["name"]}],
        "gender": row["gender"],
        "birthDate": row["birthDate"]
    }

def build_fhir_bundle(entries):
    return {
        "resourceType": "Bundle",
        "type": "batch",
        "entry": entries
    }

def main():
    seen_identifiers = set()
    bundle_entries = []
    error_entries = []

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_BUNDLE), exist_ok=True)

    with open(INPUT_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not is_valid_row(row):
                error_entries.append({**row, "error": "Missing required fields"})
                continue
            if row["identifier"] in seen_identifiers:
                error_entries.append({**row, "error": "Duplicate identifier"})
                continue

            seen_identifiers.add(row["identifier"])

            resource = convert_to_patient_resource(row)
            bundle_entries.append({
                "request": {"method": "POST", "url": "Patient"},
                "resource": resource
            })

    # Create and write bundle JSON to file
    bundle = build_fhir_bundle(bundle_entries)
    with open(OUTPUT_BUNDLE, "w") as f:
        json.dump(bundle, f, indent=2)

    # Write error logs as CSV if any
    if error_entries:
        error_fieldnames = list(error_entries[0].keys())
        with open(ERROR_LOG, "w", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=error_fieldnames)
            writer.writeheader()
            writer.writerows(error_entries)


    print(f"\nBundle created with {len(bundle_entries)} valid entries.")
    print(f"Errors logged for {len(error_entries)} invalid entries.")

    # POST the bundle to FHIR server
    try:
        response = requests.post(f"{FHIR_BASE_HAPI_URL}", headers=HEADERS, json=bundle)
        if response.status_code in (200, 201):
            print(" Bundle successfully ingested into FHIR server.")
        else:
            print(f" Failed to upload bundle. Status: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print("Exception during POST to FHIR server:", str(e))

if __name__ == "__main__":
    main()
