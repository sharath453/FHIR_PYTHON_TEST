# config.py
FHIR_BASE_FIRELY_URL = 'https://server.fire.ly'
FHIR_BASE_HAPI_URL = 'http://hapi.fhir.org/baseR4'
HEADERS = {
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json"
}
INPUT_CSV = "input/sample_file_DEMO.csv"
OUTPUT_BUNDLE = "output/patient_bundle.json"
ERROR_LOG = "output/error_log.csv"
LEARNER_NAME = 'Devesh'
OUTPUT_BUNDLE_FILTERED = 'output/filtered_bundle.json'
OUTPUT_RESOURCE_FILE_FILTERED = 'output/filtered_resource_elements.csv'
COVERAGE_IDENTIFIER_TYPE_SYSTEM = 'http://terminology.hl7.org/CodeSystem/v2-0203'