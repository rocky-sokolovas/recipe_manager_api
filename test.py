import requests
import json

url = "http://127.0.0.1:8000/ingredients"

# The data you want to send
data = {
  "name": "Tofu, Firm",
  "description": "Soybean curd, high in protein.",
  "unit": "g",
  "calories": 76.0,
  "protein": 8.0,
  "fat": 4.8,
  "carbs": 1.9
}

# The requests library automatically converts the Python dictionary to JSON
try:
    response = requests.post(url, json=data)

    # Check the status code
    response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))

except requests.exceptions.HTTPError as errh:
    print(f"HTTP Error: {errh}")
    print(f"Response Content: {response.text}")
except requests.exceptions.ConnectionError as errc:
    print(f"Error Connecting: {errc}")
except requests.exceptions.Timeout as errt:
    print(f"Timeout Error: {errt}")
except requests.exceptions.RequestException as err:
    print(f"An unexpected error occurred: {err}")
