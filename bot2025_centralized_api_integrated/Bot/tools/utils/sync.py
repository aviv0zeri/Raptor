import requests

# Disable SSL certificate validation (for testing)
response = requests.get("http://worldtimeapi.org/api/ip", verify=False)

if response.status_code == 200:
    data = response.json()
    current_time = data['datetime']
    print(f"Current time fetched: {current_time}")
else:
    print("Error fetching time from API.")
