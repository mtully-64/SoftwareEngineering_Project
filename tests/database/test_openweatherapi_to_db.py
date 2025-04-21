import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Append the path to the app/database directory so we can import the OpenWeatherAPI_to_DB.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'database')))

# Import for test
from OpenWeatherAPI_to_DB import fetch_and_insert_weather_data

class TestOpenWeatherAPIToDB(unittest.TestCase):
    """
    Unit tests for the OpenWeatherAPI_to_DB.py module.
    This test verifies that weather data fetched from the OpenWeather API
    is properly parsed and results in expected database insert operations.
    """

    @patch("OpenWeatherAPI_to_DB.requests.get")
    def test_weather_data_insertion(self, mock_requests_get):
        """
        Test that both current and forecast weather data are inserted into the database.
        The API response is mocked to avoid real network calls.
        """
        # Create a mock database connection
        mock_conn = MagicMock()

        # Create a fake JCDecaux-style station with location info
        fake_station = {
            "position": {"lat": 53.3, "lng": -6.2},
            "name": "Station 42",
            "number": 42
        }

        # Simulated JSON response from the OpenWeather API
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "timezone": "Europe/Dublin",
            "current": {
                "dt": 1700000000,
                "temp": 12.5,
                "feels_like": 11.2,
                "humidity": 80,
                "pressure": 1012,
                "wind_speed": 4.1,
                "wind_deg": 150,
                "weather": [{"description": "light rain"}],
                "uvi": 1.5,
                "clouds": 90,
                "visibility": 10000
            },
            "daily": [
                {
                    "dt": 1700000000,
                    "temp": {"day": 13.0, "min": 8.0, "max": 15.0},
                    "feels_like": {"day": 12.0, "night": 7.5},
                    "humidity": 78,
                    "pressure": 1010,
                    "wind_speed": 3.2,
                    "wind_deg": 145,
                    "weather": [{"description": "cloudy"}],
                    "clouds": 80,
                    "pop": 0.2,
                    "uvi": 2.1
                }
            ]
        }

        # Mock the requests.get call to return our fake response
        mock_requests_get.return_value = mock_response

        # Run the function under test
        fetch_and_insert_weather_data(mock_conn, fake_station)

        # Assert that at least 2 execute calls occurred (current + daily)
        self.assertTrue(mock_conn.execute.called)
        self.assertGreaterEqual(mock_conn.execute.call_count, 2)

if __name__ == "__main__":
    unittest.main()
