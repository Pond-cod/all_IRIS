import urllib.request
import json

def fetch_weather(lon, lat):
    url = f"http://www.7timer.info/bin/api.pl?lon={lon}&lat={lat}&product=civillight&output=json"
    print(f"Fetching data from: {url}")
    
    try:
        # User-Agent is sometimes required to avoid 403 Forbidden
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
            
            print("\n--- Raw Data ---")
            print(data)
            
            print("\n--- Pretty Printed JSON ---")
            try:
                parsed_json = json.loads(data)
                print(json.dumps(parsed_json, indent=2))
            except json.JSONDecodeError:
                print("Could not parse as JSON.")

    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    # Example coordinates for Bangkok, Thailand
    longitude = 100.5018
    latitude = 13.7563
    fetch_weather(longitude, latitude)
