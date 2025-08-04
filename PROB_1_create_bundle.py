import csv
import json
import os
import sys
from collections import defaultdict
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    FHIR_BASE_HAPI_URL as BASE_URL,
    HEADERS as REQUEST_HEADERS,
    INPUT_CSV as SOURCE_CSV,
    OUTPUT_BUNDLE as BUNDLE_OUTPUT_PATH,
    ERROR_LOG as LOG_FILE_PATH,
    LEARNER_NAME as USER_TAG
)

MANDATORY_FIELDS = ["id", "name", "status", "address_line", "address_state"]

def validate_csv_row(entry):
    return all(entry.get(field) for field in MANDATORY_FIELDS)

def transform_to_location_resource(resource_key, resource_group):
    base_record = resource_group[0]
    operation_hours = []

    for item in resource_group:
        if item.get("hours_of_operation_days_of_week"):
            try:
                operation_hours.append({
                    "daysOfWeek": [item["hours_of_operation_days_of_week"]],
                    "allDay": item["hours_of_operation_all_day"].strip().lower() == 'true'
                })
            except:
                pass

    location_payload = {
        "resourceType": "Location",
        "id": resource_key,
        "name": base_record["name"],
        "status": base_record["status"],
        "address": {
            "line": [base_record["address_line"]],
            "state": base_record["address_state"]
        },
        "meta": {
            "tag": [{
                "code": f"Learners-{USER_TAG}",
                "display": "Learners-FHIR-Assessment"
            }]
        }
    }

    if operation_hours:
        location_payload["hoursOfOperation"] = operation_hours

    if base_record.get("position_longitude") and base_record.get("position_latitude"):
        try:
            location_payload["position"] = {
                "longitude": float(base_record["position_longitude"]),
                "latitude": float(base_record["position_latitude"])
            }
        except ValueError:
            pass

    return location_payload

def assemble_fhir_bundle(resources):
    return {
        "resourceType": "Bundle",
        "type": "batch",
        "entry": resources
    }

def run_resource_ingestion_pipeline():
    unique_combinations = set()
    valid_resources = []
    error_records = []
    grouped_resources = defaultdict(list)

    os.makedirs(os.path.dirname(BUNDLE_OUTPUT_PATH), exist_ok=True)

    with open(SOURCE_CSV, newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for record in csv_reader:
            compound_key = (
                record.get("id"),
                record.get("hours_of_operation_days_of_week"),
                record.get("hours_of_operation_all_day")
            )

            if compound_key in unique_combinations:
                record["error"] = "Duplicate hours_of_operation entry"
                error_records.append(record)
                continue

            if not validate_csv_row(record):
                record["error"] = "Missing required fields"
                error_records.append(record)
                continue

            unique_combinations.add(compound_key)
            grouped_resources[record["id"]].append(record)

    for unique_id, records in grouped_resources.items():
        location_resource = transform_to_location_resource(unique_id, records)
        valid_resources.append({
            "request": {"method": "POST", "url": "Location"},
            "resource": location_resource
        })

    fhir_bundle = assemble_fhir_bundle(valid_resources)
    with open(BUNDLE_OUTPUT_PATH, "w") as bundle_file:
        json.dump(fhir_bundle, bundle_file, indent=2)

    if error_records:
        with open(LOG_FILE_PATH, "w", newline='') as error_file:
            writer = csv.DictWriter(error_file, fieldnames=error_records[0].keys())
            writer.writeheader()
            writer.writerows(error_records)

    print(f"\nBundle created with {len(valid_resources)} Location entries.")
    print(f"{len(error_records)} error entries logged.")

    try:
        response = requests.post(BASE_URL, headers=REQUEST_HEADERS, json=fhir_bundle)
        if response.status_code in (200, 201):
            print("Bundle successfully uploaded to HAPI FHIR server.")
        else:
            print(f"Failed to upload bundle. Status Code: {response.status_code}")
            print("Server Response:", response.text)
    except Exception as ex:
        print("Error during upload:", str(ex))

if __name__ == "__main__":
    run_resource_ingestion_pipeline()
