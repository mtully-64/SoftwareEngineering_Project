import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the path to the database module so we can import from app/database/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'database')))

from OpenWeatherAPI_to_DB import fetch_and_insert_weather_data


class TestOpenWeatherToFile(unittest.TestCase):
    """
    This test case verifies that weather data fetched from the OpenWeather API
    is correctly handled and prepared for insertion or file-based storage.
    The actual HTTP request and DB connection are mocked for isolated testing.
    """

    @patch("OpenWeatherAPI_to_DB.requests.get")
    def test_weather_data_handling(self, mock_get):
        """
        Tests whether the fetch_and_insert_weather_data function correctly processes
        a typical OpenWeather API response, and ensures that the function performs
        expected logic on the weather data.
        """

        # Mock a connection object to simulate SQL/file-like execution
        mock_conn = MagicMock()

        # Simulate a station input (normally used to pass lat/lon and ID)
        fake_station = {
            "position": {"lat": 53.3, "lng": -6.2},
            "name": "Station 42",
            "number": 42
        }

        # Set up a mocked API response to mimic OpenWeather's structure
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

        # Assign mocked response to the requests.get call
        mock_get.return_value = mock_response

        # Call the function with mock connection and station
        fetch_and_insert_weather_data(mock_conn, fake_station)

        # Assert that mock_conn.execute() was called, meaning data was processed
        self.assertTrue(mock_conn.execute.called)

        # Assert multiple executions (e.g., current + forecast insertions)
        self.assertGreaterEqual(mock_conn.execute.call_count, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
