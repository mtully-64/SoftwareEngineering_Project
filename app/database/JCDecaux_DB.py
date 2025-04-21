from sqlalchemy import create_engine, text
import JCD_DB_Info

# Load credentials
USER = JCD_DB_Info.USER
PASSWORD = JCD_DB_Info.PASSWORD
PORT = JCD_DB_Info.PORT
DB = JCD_DB_Info.DB
URI = JCD_DB_Info.URI

# Use PyMySQL instead of MySQLdb since lecture material didnt work
connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{URI}:{PORT}/"
engine = create_engine(connection_string, echo=True)

# MySQL command to create the 'station' table
station_sql = text("""
CREATE TABLE IF NOT EXISTS station (
    number INTEGER NOT NULL,
    address VARCHAR(128),
    banking INTEGER,
    bike_stands INTEGER,
    name VARCHAR(256),
    status VARCHAR(128),
    position_lat FLOAT,
    position_lng FLOAT,
    PRIMARY KEY (number)
)
""")

# MySQL command to create the 'availability' table
availability_sql = text("""
CREATE TABLE IF NOT EXISTS availability (
    number INTEGER NOT NULL,
    available_bikes INTEGER,
    available_bike_stands INTEGER,
    last_update DATETIME NOT NULL,
    status VARCHAR(128),
    PRIMARY KEY (number, last_update),
    FOREIGN KEY (number) REFERENCES station(number) ON DELETE CASCADE
)
""")

try:
    with engine.connect() as connection:
        print("Successfully connected!")

        # Create the database if it doesn't exist
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB}`;"))
        print(f"Database `{DB}` created or already exists.")

    # Update connection string to include the database
    engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{URI}:{PORT}/{DB}", echo=True)

    with engine.connect() as connection:
        # Show all database variables
        result = connection.execute(text("SHOW VARIABLES;"))
        print("\nMySQL Variables:")
        for row in result:
            print(row)
except Exception as e:
    print("Connection failed:", e)

# Ensure 'station' table is created
try:
    with engine.connect() as connection:
        connection.execute(station_sql)
        print("'station' table created successfully.")
except Exception as e:
    print("Error creating 'station' table:", e)

# Ensure 'availability' table created
try:
    with engine.connect() as connection:
        connection.execute(availability_sql)
        print("'availability' table created successfully.")
except Exception as e:
    print("Error creating 'availability' table:", e)
