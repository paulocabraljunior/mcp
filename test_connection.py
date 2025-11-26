
import requests
import sys

url = "http://127.0.0.1:8000/"
print(f"Testing connection to {url}...")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
