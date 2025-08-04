import requests
import json
import csv
import os
import sys

# Add root directory to Python path for importing config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import constants from config
from config import FHIR_BASE_FIRELY_URL, HEADERS, OUTPUT_BUNDLE_FILTERED,OUTPUT_RESOURCE_FILE_FILTERED


def fetch_filtered_patients(gender=None, last_updated_after=None):
    query_params = []

    if gender:
        query_params.append(f"gender={gender}")
    if last_updated_after:
        query_params.append(f"_lastUpdated=ge{last_updated_after}")

    query_params.append("_count=10")
    query_string = "&".join(query_params)
    url = f"{FHIR_BASE_FIRELY_URL}/Patient?{query_string}"

    all_patients = []

    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        bundle = response.json()
        entries = bundle.get("entry", [])
        all_patients.extend(entries)

        # Get the next page link
        next_link = None
        for link in bundle.get("link", []):
            if link.get("relation") == "next":
                next_link = link.get("url")
                break

        url = next_link

    return all_patients


def save_json(bundle_data, filename):
    with open(filename, "w") as f:
        json.dump(bundle_data, f, indent=2)
    print(f"JSON saved to: {filename}")


def write_csv(patients, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["Full Name", "Gender", "BirthDate"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in patients:
            resource = entry.get("resource", {})
            gender = resource.get("gender", "")
            birthdate = resource.get("birthDate", "")
            names = resource.get("name", [])

            if names:
                given = " ".join(names[0].get("given", []))
                family = names[0].get("family", "")
                full_name = f"{given} {family}".strip()
            else:
                full_name = "(No Name)"

            writer.writerow({
                "Full Name": full_name,
                "Gender": gender,
                "BirthDate": birthdate
            })

    print(f" CSV saved to: {filename}")


# === Run the program ===
patients = fetch_filtered_patients(gender="male", last_updated_after="2025-07-28")

# Save full bundle
save_json(patients, OUTPUT_BUNDLE_FILTERED)

# Save key patient details as CSV
write_csv(patients, OUTPUT_RESOURCE_FILE_FILTERED)
