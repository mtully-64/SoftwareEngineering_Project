import requests
import traceback
import json
import sqlalchemy #this stays here
from sqlalchemy import create_engine, text as sql_text  # I have to do this for conflict checks of functions
import JCD_DB_Info
import JCD_API_Info

def stations_to_db(text_data, engine): 
    """Parse, print, and insert station data into the database. Also the code is built to avoid duplicates."""
    
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
                    station.get('status', 'Unknown')
                )

                print(vals) 
                
                # Check if the station already exists in the 'station' table
                check_query = "SELECT COUNT(*) FROM station WHERE name = :name" 
                query_result = conn.execute(sql_text(check_query), {"name": vals[3]}).scalar()

                if query_result == 0:
                    insert_query = """
                        INSERT INTO station (address, banking, bike_stands, name, status)
                        VALUES (:address, :banking, :bike_stands, :name, :status)
                    """

 
                    conn.execute(sqlalchemy.text(insert_query), {
                        "address": vals[0], 
                        "banking": vals[1], 
                        "bike_stands": vals[2],
                        "name": vals[3], 
                        "status": vals[4]
                    })

                    print(f"Inserted: {vals[3]}")
                else:
                    print(f"Skipped (already exists): {vals[3]}")
            
            conn.commit()
        
        print("\nData insertion completed!\n")

    except Exception as e:
        print("Error processing data:", e)
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
