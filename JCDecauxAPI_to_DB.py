import requests
import traceback
import json
import sqlalchemy  
from sqlalchemy import create_engine, text as sql_text  
import JCD_DB_Info
import JCD_API_Info
from datetime import datetime  

def stations_to_db(text_data, engine): 
    """Parse, print, and insert station data into the database while avoiding duplicates.
       Also inserts new availability data into the availability table.
    """
    try:
        stations = json.loads(text_data)
        print(f"Loaded {len(stations)} stations\n")

        with engine.connect() as conn:
            for station in stations:
                vals = (
                    station.get('address', 'N/A'),
                    int(station.get('banking', 0)),
                    int(station.get('bike_stands', 0)),
                    station.get('name', 'Unknown'),
                    station.get('status', 'Unknown'),
                    float(station.get('position', {}).get('lat', 0.0)), 
                    float(station.get('position', {}).get('lng', 0.0))  
                )

                # Check if the station already exists
                check_query = "SELECT COUNT(*) FROM station WHERE number = :number"
                query_result = conn.execute(sql_text(check_query), {"number": station.get('number')}).scalar()


                if query_result == 0:
                    insert_query = """
                        INSERT INTO station (address, banking, bike_stands, name, status, position_lat, position_lng)
                        VALUES (:address, :banking, :bike_stands, :name, :status, :position_lat, :position_lng)
                    """
                    conn.execute(sql_text(insert_query), {
                        "address": vals[0], 
                        "banking": vals[1], 
                        "bike_stands": vals[2],
                        "name": vals[3], 
                        "status": vals[4],
                        "position_lat": vals[5],
                        "position_lng": vals[6]
                    })
                    print(f"Inserted new station: {vals[3]}")
                else:
                    print(f"Skipped (already exists): {vals[3]}")

                # Always insert a new availability record
                insert_availability(conn, station)
            
            conn.commit()
        
        print("\nData insertion completed!\n")
    except Exception as e:
        print("Error processing data:", e)
        print(traceback.format_exc())

def insert_availability(conn, station):
    """Insert availability data into the database, keeping a full history of bike availability."""
    try:
        number = int(station.get('number', 0))
        available_bikes = int(station.get('available_bikes', 0))
        available_bike_stands = int(station.get('available_bike_stands', 0))
        status = station.get('status', 'Unknown')
        
        # Convert timestamp from milliseconds to a MySQL DATETIME format
        last_update_ts = int(station.get('last_update', 0)) // 1000  # Convert to seconds
        last_update = datetime.utcfromtimestamp(last_update_ts).strftime('%Y-%m-%d %H:%M:%S')

        # **NEW: Always insert a new row, no matter what**
        insert_query = """
            INSERT INTO availability (number, available_bikes, available_bike_stands, last_update, status)
            VALUES (:number, :available_bikes, :available_bike_stands, :last_update, :status)
        """
        conn.execute(sql_text(insert_query), {
            "number": number,
            "available_bikes": available_bikes,
            "available_bike_stands": available_bike_stands,
            "last_update": last_update,
            "status": status
        })
        print(f"Inserted availability for station {number} at {last_update}")

    except Exception as e:
        print(f"Error inserting availability for station {station.get('number')}: {e}")
        print(traceback.format_exc())

def main():
    """Fetch JCDecaux station data once and insert into the database."""
    USER = JCD_DB_Info.USER
    PASSWORD = JCD_DB_Info.PASSWORD
    PORT = JCD_DB_Info.PORT
    DB = JCD_DB_Info.DB
    URI = JCD_DB_Info.URI

    connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{URI}:{PORT}/{DB}"
    engine = create_engine(connection_string, echo=True)

    try:
        response = requests.get(JCD_API_Info.STATIONS_URI, params={"apiKey": JCD_API_Info.JCKEY, "contract": JCD_API_Info.NAME})
        response.raise_for_status()
        stations_to_db(response.text, engine)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    main()
