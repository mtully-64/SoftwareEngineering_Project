import JCD_API_Info
import requests
import json
import os
import datetime
import time
import traceback

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_PATH = os.path.join(SCRIPT_DIR, "JCD_API_Data")

# Ensure the folder always exists in the same location as the script
if not os.path.exists(FOLDER_PATH):
    os.mkdir(FOLDER_PATH)
    print(f"Folder '{FOLDER_PATH}' Created!")
else:
    print(f"Folder '{FOLDER_PATH}' Already Exists.")

def write_to_txtfile(text):
    """Function used to store text in a file, pulled from the API request"""
    
    # Create the folder if it doesn't exist (ensuring in function scope too)
    if not os.path.exists(FOLDER_PATH):
        os.mkdir(FOLDER_PATH)
    
    # Format timestamp correctly (done for Windows)
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Write data to file
    file_path = os.path.join(FOLDER_PATH, f"bikes_{now}.txt")
    with open(file_path, "w") as f:
        f.write(text)

# Main code
def main():
    # In an infinite loop, every 5mins get the API data and insert it into a text file
    while True:
        try:
            r = requests.get(JCD_API_Info.STATIONS_URI, params={"apiKey": JCD_API_Info.JCKEY, "contract": JCD_API_Info.NAME})
            print(r)
            
            if r.status_code == 200:
                write_to_txtfile(r.text)
            else:
                print(f"Failed to fetch data. Status code: {r.status_code}")

            time.sleep(5*60)  # Wait 5 minutes before next request, this will be taken out for replacement by cromp
        except:
            # If there is a problem, then print the traceback
            print(traceback.format_exc())

# learned this in my undergrad
if __name__ == "__main__":
    main()
