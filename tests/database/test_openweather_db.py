import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Append the path to the app/database directory so we can import OpenWeather_DB
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'database')))

# Import for the test
import OpenWeather_DB

class TestOpenWeatherDB(unittest.TestCase):
    """
    Unit tests for the OpenWeather_DB.py module.
    These tests confirm that the SQL creation statements for weather-related tables in the local SQL database
    are executed correctly using a mocked database connection.
    """

    @patch("OpenWeather_DB.engine.connect")
    def test_create_current_weather_table(self, mock_connect):
        """
        Test that the SQL for creating the 'current_weather' table executes successfully.
        """
        # Create a mock connection object
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute the SQL creation statement
        OpenWeather_DB.current_weather_sql.execute(mock_conn)

        # Assert that the SQL execution method was called
        mock_conn.execute.assert_called()

    @patch("OpenWeather_DB.engine.connect")
    def test_create_daily_forecast_table(self, mock_connect):
        """
        Test that the SQL for creating the 'daily_forecast' table executes successfully.
        """
        # Create a mock connection object
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute the SQL creation statement
        OpenWeather_DB.daily_forecast_sql.execute(mock_conn)

        # Assert that the SQL execution method was called
        mock_conn.execute.assert_called()

if __name__ == "__main__":
    unittest.main()