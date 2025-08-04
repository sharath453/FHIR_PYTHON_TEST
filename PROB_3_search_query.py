import requests
import json
import os
import csv

FHIR_BASE_URL = "https://server.fire.ly"
PAGE_SIZE = 50
HEADERS = {"Accept": "application/fhir+json"}

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

JSON_FILE = os.path.join(OUTPUT_DIR, "deceased_patients.json")
CSV_FILE = os.path.join(OUTPUT_DIR, "deceased_patients.csv")


def fetch_all_deceased_patients():
    url = f"{FHIR_BASE_URL}/Patient?deceased=true&birthdate=ge1945-01-01&birthdate=le1985-12-31&_count={PAGE_SIZE}"
    all_entries = []

    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching patients: {response.status_code}")
 

# PROB_3_search_query.py
# Fetch deceased patients born between 1945 and 1985 from Firely server, save as JSON and CSV

import requests
import json
import os
import csv

FHIR_BASE_URL = "https://server.fire.ly"
PAGE_SIZE = 50
HEADERS = {"Accept": "application/fhir+json"}

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

JSON_FILE = os.path.join(OUTPUT_DIR, "deceased_patients.json")
CSV_FILE = os.path.join(OUTPUT_DIR, "deceased_patients.csv")

def fetch_all_deceased_patients():
    url = f"{FHIR_BASE_URL}/Patient?deceased=true&birthdate=ge1945-01-01&birthdate=le1985-12-31&_count={PAGE_SIZE}"
    all_entries = []
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching patients: {response.status_code}")
            break
        bundle = response.json()
        entries = bundle.get("entry", [])
        print(f"Fetched {len(entries)} patients from {url}")
        if not entries:
            break
        all_entries.extend(entries)
        # Get next page link if present
        next_url = None
        for link in bundle.get("link", []):
            if link.get("relation") == "next":
                next_url = link.get("url")
                break
        url = next_url
    return all_entries

def save_json(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved JSON to {filepath}")

def write_csv(patients, filepath):
    with open(filepath, "w", newline="") as csvfile:
        fieldnames = ["Patient ID", "Name", "Gender", "Birthdate", "DeceasedDateTime"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in patients:
            resource = entry.get("resource", {})
            patient_id = resource.get("id", "")
            gender = resource.get("gender", "")
            birthdate = resource.get("birthDate", "")
            # Extract name - try first available
            names = resource.get("name", [])
            if names:
                name_obj = names[0]
                given = " ".join(name_obj.get("given", []))
                family = name_obj.get("family", "")
                full_name = f"{given} {family}".strip()
            else:
                full_name = "(No Name)"
            # Deceased can be boolean or datetime; prefer datetime if available
            deceased = resource.get("deceasedDateTime")
            if deceased is None:
                deceased_bool = resource.get("deceasedBoolean")
                deceased = str(deceased_bool) if deceased_bool is not None else ""
            writer.writerow({
                "Patient ID": patient_id,
                "Name": full_name,
                "Gender": gender,
                "Birthdate": birthdate,
                "DeceasedDateTime": deceased
            })
    print(f"Saved CSV to {filepath}")

def main():
    print("Fetching deceased patients with pagination...")
    patients = fetch_all_deceased_patients()
    # Save full response bundle (combine entries into one bundle)
    bundle = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": patients
    }
    save_json(bundle, JSON_FILE)
    # Write key data to CSV
    write_csv(patients, CSV_FILE)

if __name__ == "__main__":
    main()