from sqlalchemy import create_engine, text
import JCD_DB_Info

# Load credentials
USER = JCD_DB_Info.USER
PASSWORD = JCD_DB_Info.PASSWORD
PORT = JCD_DB_Info.PORT
DB = JCD_DB_Info.DB
URI = JCD_DB_Info.URI

# Use PyMySQL for database connection
connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{URI}:{PORT}/"
engine = create_engine(connection_string, echo=True)

# MySQL command to create the 'current_weather' table
current_weather_sql = text("""
CREATE TABLE IF NOT EXISTS current_weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    temperature FLOAT NOT NULL,
    feels_like FLOAT NOT NULL,
    humidity INTEGER NOT NULL,
    pressure INTEGER NOT NULL,
    wind_speed FLOAT NOT NULL,
    wind_direction INTEGER NOT NULL,
    weather_description VARCHAR(128),
    uvi FLOAT NOT NULL,
    clouds_percentage INTEGER NOT NULL,
    visibility INTEGER NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    timezone VARCHAR(64),
    location_name VARCHAR(128)
)
""")

# MySQL command to create the 'daily_forecast' table
daily_forecast_sql = text("""
CREATE TABLE IF NOT EXISTS daily_forecast (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    temperature_day FLOAT NOT NULL,
    temperature_min FLOAT NOT NULL,
    temperature_max FLOAT NOT NULL,
    feels_like_day FLOAT NOT NULL,
    feels_like_night FLOAT NOT NULL,
    humidity INTEGER NOT NULL,
    pressure INTEGER NOT NULL,
    wind_speed FLOAT NOT NULL,
    wind_direction INTEGER NOT NULL,
    weather_description VARCHAR(128),
    clouds_percentage INTEGER NOT NULL,
    precipitation_probability FLOAT NOT NULL,
    uvi FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    timezone VARCHAR(64),
    location_name VARCHAR(128)
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

# Ensure 'current_weather' table is created
try:
    with engine.connect() as connection:
        connection.execute(current_weather_sql)
        print("'current_weather' table created successfully.")
except Exception as e:
    print("Error creating 'current_weather' table:", e)

# Ensure 'daily_forecast' table is created
try:
    with engine.connect() as connection:
        connection.execute(daily_forecast_sql)
        print("'daily_forecast' table created successfully.")
except Exception as e:
    print("Error creating 'daily_forecast' table:", e)
