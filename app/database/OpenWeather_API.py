from OpenWeather_API_Info import OpenWeather_KEY
import requests
import json
import os
import datetime
import time
import traceback

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_PATH = os.path.join(SCRIPT_DIR, "Weather_API_Data")

# Ensure the folder always exists in the same location as the script
if not os.path.exists(FOLDER_PATH):
    os.mkdir(FOLDER_PATH)
    print(f"Folder '{FOLDER_PATH}' Created!")
else:
    print(f"Folder '{FOLDER_PATH}' Already Exists.")

def write_to_txtfile(text):
    """Function used to store text in a file, pulled from the API request"""
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(FOLDER_PATH, f"weather_{now}.txt")
    with open(file_path, "w") as f:
        f.write(text)

def fetch_weather_data(lat, lon):
    """Fetch weather data from OpenWeather API"""
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&appid={OpenWeather_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch weather data for ({lat}, {lon}). Status code: {response.status_code}")
        return None

# Main Code
def main():
    lat, lon = 53.3498, -6.2603 # Dublin City Center
    while True:
        try:
            data = fetch_weather_data(lat, lon)
            if data:
                write_to_txtfile(json.dumps(data, indent=4))
            
            time.sleep(5 * 60)  # Wait 5 minutes before next request
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print(traceback.format_exc())

if __name__ == "__main__":
    main()