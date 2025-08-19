import requests
import os
import json
import sys

github_username = os.environ['GITHUB_ACTOR']
api_url = "http://89.169.163.78:8000/save_result"
timings_json = os.environ.get('TIMINGS_JSON', '{}')
timestamp = os.environ.get('TIMESTAMP')

try:
    timings = json.loads(timings_json)
except json.JSONDecodeError:
    timings = {}

if not timings:
    print("No timings to save")
    sys.exit(0)

payload = {
    "github_username": github_username,
    "timings": timings,
    "timestamp": timestamp
}

try:
    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        print("✅ Results saved successfully")
    else:
        print(f"⚠️ Failed to save results: {response.status_code} {response.text}")
except Exception as e:
    print(f"⚠️ Error saving results: {str(e)}")
