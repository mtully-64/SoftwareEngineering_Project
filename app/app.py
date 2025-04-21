# Import modules utilised in app
from flask import Flask, render_template, redirect, request, session, url_for, jsonify
import json
import requests
import firebase_admin
import os
import pandas as pd
from datetime import datetime
import pickle
from firebase_admin import credentials, auth
import numpy as np
from sqlalchemy import create_engine
from database import JCD_DB_Info, JCD_DB_local

# Please first import the sql file in database folder!
USER = JCD_DB_local.USER
PASSWORD = JCD_DB_local.PASSWORD
PORT = JCD_DB_local.PORT
DB = JCD_DB_local.DB
URI = JCD_DB_local.URI

connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{URI}:{PORT}/{DB}"
engine = create_engine(connection_string, echo=True)

# Load historical data from MySQL
query = f"""
    SELECT number, available_bikes, available_bike_stands, last_update, status
    FROM daily_trends"""

HISTORY_DF = pd.read_sql(query, con=engine)
HISTORY_DF['last_update'] = pd.to_datetime(HISTORY_DF['last_update'], errors='coerce')
HISTORY_DF.dropna(subset=['last_update'], inplace=True)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

def load_config():
    # Load config.json relative to the app.py file itself
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path) as config_file:
        return json.load(config_file)

config = load_config()
JCDECAUX_API_KEY = config["JCDECAUX_API_KEY"]
OPENWEATHER_API_KEY = config["OPENWEATHER_API_KEY"]
GOOGLE_MAPS_API_KEY = config["GOOGLE_MAPS_API_KEY"]

# City contract name for JCDecaux bike-sharing API
CONTRACT = "dublin"
# API URL for fetching bike station data in Dublin
BIKE_API_URL = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT}&apiKey={JCDECAUX_API_KEY}"

# Initialize Firebase Admin SDK
def initialize_firebase():
    cred_path = os.path.join(os.path.dirname(__file__), "dublinbikes-firebase-config.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

## Load the machine learning model
model_path = os.path.join(os.path.dirname(__file__), "machine_learning", "Dubike_random_forest_model.joblib")
with open(model_path, "rb") as file:
    model = pickle.load(file)

initialize_firebase()

#### Routes ####

@app.route("/")
def home():
    """
    Redirect users based on authentication status.
    """
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    """
    Display dashboard with bike station data.
    """
    if "user" not in session:
        return redirect(url_for("login"))
    
    first_name = session.get("first_name", "User")
    bike_stations = fetch_bike_stations()
    return render_template("index.html", title="Dublin Bikes", stations=bike_stations, google_maps_api_key=GOOGLE_MAPS_API_KEY, first_name=first_name)

@app.route("/api/station_history")
def get_station_history():
    station_id = request.args.get("station_id")
    if not station_id:
        return jsonify({"error": "Missing station_id"}), 400

    try:
        station_id = int(station_id)
    except ValueError:
        return jsonify({"error": "Invalid station_id"}), 400

    filtered_df = HISTORY_DF[HISTORY_DF["number"] == station_id].copy()

    filtered_df = filtered_df.sort_values("last_update")

    result = []
    for _, row in filtered_df.iterrows():
        result.append({
            "time": row["last_update"].strftime("%Y-%m-%dT%H:%M:%S"),
            "bikes": row["available_bikes"],
            "stands": row["available_bike_stands"]
        })

    return jsonify(result)

## Define a route for predictions ## 
@app.route("/predict", methods=["GET"])
def predict():
    try:
        date = request.args.get("date")
        time = request.args.get("time")
        station_id = request.args.get("station_id")

        if not date or not time or not station_id:
            return jsonify({"error": "Missing date, time, or station_id parameter"}), 400

        # get the lat and lng for target station
        stations = fetch_bike_stations()
        station = next((s for s in stations if str(s["number"]) == str(station_id)), None)
        if not station:
            return jsonify({"error": "Station not found"}), 404

        lat = station["position"]["lat"]
        lon = station["position"]["lng"]

        # call openweather api
        weather_data = fetch_openweather_forecast(lat, lon, date, time)

        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        day = dt.weekday()

        input_features = [
            int(station_id),
            weather_data["max_temperature"],
            weather_data["min_temperature"],
            weather_data["humidity"],
            weather_data["pressure"],
            hour,
            day,
        ]

        columns = ["station_id", "max_temperature", "min_temperature", "humidity", "pressure", "hour", "day"]
        input_df = pd.DataFrame([input_features], columns=columns)
        prediction = model.predict(input_df)

        return jsonify({"predicted_available_bikes": round(float(prediction[0]))})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/predict_week", methods=["GET"])
def predict_week():
    try:
        station_id = request.args.get("station_id")
        if not station_id:
            return jsonify({"error": "Missing station_id"}), 400

        stations = fetch_bike_stations()
        station = next((s for s in stations if str(s["number"]) == str(station_id)), None)
        if not station:
            return jsonify({"error": "Station not found"}), 404

        lat = station["position"]["lat"]
        lon = station["position"]["lng"]

        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch weather forecast"}), 500

        data = response.json()
        daily_data = data.get("daily", [])
        results = []
        for forecast in daily_data:
            from datetime import timezone
            timestamp = datetime.fromtimestamp(forecast["dt"], tz=timezone.utc)
            day_of_week = timestamp.weekday()
            hour = 12

            max_temp = forecast["temp"]["max"]
            min_temp = forecast["temp"]["min"]
            humidity = forecast.get("humidity", 0)
            pressure = forecast.get("pressure", 0)

            input_features = [
                int(station_id),
                max_temp,
                min_temp,
                humidity,
                pressure,
                hour,
                day_of_week,
            ]

            columns = ["station_id", "max_temperature", "min_temperature", "humidity", "pressure", "hour", "day"]
            input_df = pd.DataFrame([input_features], columns=columns)
            predicted_bikes = float(model.predict(input_df)[0])

            results.append({
                "time": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "predicted_bikes": predicted_bikes
            })

        return jsonify(results)

    except Exception as e:
        print("Prediction error:", str(e))
        return jsonify({"error": str(e)}), 500

## Define a route for log in ##

@app.route("/login")
def login():
    """
    Render login page.
    """
    return render_template("login.html")

@app.route("/logout")
def logout():
    """
    Logout user by removing session data.
    """
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/api/weather")
def get_weather():
    """
    Fetch real-time weather data from OpenWeather API.
    """
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    return jsonify(fetch_weather_data(lat, lon))

@app.route("/api/bike_stations")
def get_bike_stations():
    """
    Fetch real-time bike station data for Dublin.
    """
    return jsonify(fetch_bike_stations())

@app.route("/api/google-maps-key")
def get_google_maps_key():
    """
    Securely return the Google Maps API key.
    """
    return jsonify({"apiKey": GOOGLE_MAPS_API_KEY})

@app.route("/verify_login", methods=["POST"])
def verify_login():
    """
    Verify user login with Firebase authentication.
    """
    try:
        data = request.json
        id_token = data.get("idToken")
        if not id_token:
            return jsonify({"success": False, "error": "Missing token"}), 401
        
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]
        session["user"] = user_id  # Store session

        return jsonify({"success": True, "user_id": user_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401

@app.route("/signup")
def signup():
    """
    Render the sign-up page.
    """
    return render_template("sign-up.html")

### Helper Functions ###

def fetch_weather_data(lat, lon):
    """
    Fetch weather data for given latitude and longitude.
    """
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    return requests.get(weather_url).json()


def fetch_bike_stations():
    """
    Fetch bike station data from JCDecaux API.
    """
    return requests.get(BIKE_API_URL).json()

def fetch_openweather_forecast(lat, lon, target_date_str, target_time_str):
    """
    Fetch hourly forecast from OpenWeather 3.0 API and find the record
    closest to the requested datetime.
    """
    from datetime import datetime
    target_dt = datetime.strptime(f"{target_date_str} {target_time_str}", "%Y-%m-%d %H:%M:%S")

    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,daily,alerts&units=metric&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url).json()

    if "hourly" not in response:
        raise Exception("No hourly forecast data found")

    closest_forecast = None
    min_diff = float("inf")

    for forecast in response["hourly"]:
        forecast_time = datetime.fromtimestamp(forecast["dt"])
        diff = abs((forecast_time - target_dt).total_seconds())
        if diff < min_diff:
            min_diff = diff
            closest_forecast = forecast

    if closest_forecast is None:
        raise Exception("No matching forecast found")

    return {
        "max_temperature": closest_forecast["temp"],
        "min_temperature": closest_forecast["temp"],
        "humidity": closest_forecast["humidity"],
        "pressure": closest_forecast["pressure"]
    }


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) # Added the host of 0.0.0.0 and port 5000, to make this public from EC2
