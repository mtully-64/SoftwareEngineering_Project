import requests
import traceback
import json
import sqlalchemy
from sqlalchemy import create_engine, text as sql_text
import JCD_DB_local
import JCD_API_Info
from datetime import datetime
import time

def stations_to_db(text_data, engine):
    """
    Parse, log, and insert station data into the local SQL database while avoiding duplicates.
    If no database engine is provided, fallback to writing station data into a local JSON file.
    """
    try:
        stations = json.loads(text_data)
        print(f"Loaded {len(stations)} stations\n")

        if engine is None:
            with open("stations_output.json", "w") as f:
                json.dump(stations, f, indent=2)
            print("Saved station data to stations_output.json")
            return

        # Transactional block using engine.begin() (auto-commits or rolls back on exception)
        with engine.begin() as conn:
            for station in stations:
                station_number = station.get('number')
                try:
                    vals = {
                        "number": station_number,
                        "address": station.get('address', 'N/A'),
                        "banking": int(station.get('banking', 0)) if station.get('banking') is not None else 0,
                        "bike_stands": int(station.get('bike_stands', 0)) if station.get('bike_stands') is not None else 0,
                        "name": station.get('name', 'Unknown'),
                        "status": station.get('status', 'Unknown'),
                        "position_lat": float(station.get('position', {}).get('lat', 0.0)),
                        "position_lng": float(station.get('position', {}).get('lng', 0.0))
                    }
                except Exception as conv_e:
                    print(f"Conversion error, skipping station {station_number}: {conv_e}")
                    continue

                # Check if station already exists
                check_query = "SELECT COUNT(*) FROM station WHERE number = :number"
                query_result = conn.execute(sql_text(check_query), {"number": station_number}).scalar()

                if query_result == 0:
                    insert_query = """
                        INSERT INTO station (number, address, banking, bike_stands, name, status, position_lat, position_lng)
                        VALUES (:number, :address, :banking, :bike_stands, :name, :status, :position_lat, :position_lng)
                    """
                    conn.execute(sql_text(insert_query), vals)
                    print(f"Inserted new station: {vals['name']}")
                else:
                    print(f"Skipped (already exists): {vals['name']}")

                # Always insert new availability record
                insert_availability(conn, station)

        print("\nData insertion completed!\n")
    except Exception as e:
        print("Error processing data:", e)
        print(traceback.format_exc())

def insert_availability(conn, station):
    """
    Insert availability data into the database, avoiding duplicates using INSERT IGNORE.
    """
    try:
        number = int(station.get('number', 0))
        available_bikes = int(station.get('available_bikes', 0)) if station.get('available_bikes') is not None else 0
        available_bike_stands = int(station.get('available_bike_stands', 0)) if station.get('available_bike_stands') is not None else 0
        status = station.get('status', 'Unknown')
        last_update = int(station.get('last_update', 0))  # keep as UNIX ms timestamp

        insert_query = """
            INSERT IGNORE INTO availability (number, available_bikes, available_bike_stands, last_update, status)
            VALUES (:number, :available_bikes, :available_bike_stands, :last_update, :status)
        """

        result = conn.execute(sql_text(insert_query), {
            "number": number,
            "available_bikes": available_bikes,
            "available_bike_stands": available_bike_stands,
            "last_update": last_update,
            "status": status
        })

        if result.rowcount == 1:
            print(f"Inserted availability for station {number} at {last_update}")
        else:
            print(f"Skipped duplicate for station {number} at {last_update}")

    except Exception as e:
        print(f"Error inserting availability for station {station.get('number')}: {e}")
        print(traceback.format_exc())

def main():
    """
    Fetch JCDecaux station data and insert into the local MySQL database.
    """
    USER = JCD_DB_local.USER
    PASSWORD = JCD_DB_local.PASSWORD
    PORT = JCD_DB_local.PORT
    DB = JCD_DB_local.DB
    URI = JCD_DB_local.URI

    connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{URI}:{PORT}/{DB}"
    engine = create_engine(connection_string, echo=True)

    try:
        response = requests.get(JCD_API_Info.STATIONS_URI, params={"apiKey": JCD_API_Info.JCKEY, "contract": JCD_API_Info.NAME})
        response.raise_for_status()
        stations_to_db(response.text, engine)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    while True:
        print("Fetching and writing data...")
        main()
        print("Sleeping for 5 minutes...\n")
        time.sleep(300)
