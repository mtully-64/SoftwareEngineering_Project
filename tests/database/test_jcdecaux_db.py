import sys
import os
import unittest
from unittest.mock import MagicMock
import json

# Add the app/database directory to sys.path to enable imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'database')))

# Import the JCDecaux data insertion logic
import JCDecauxAPI_to_DB


class TestJCDecauxDB(unittest.TestCase):
    """
    Unit test for JCDecauxAPI_to_DB module.
    This test verifies that the function stations_to_db correctly parses input JSON and triggers
    appropriate SQL insertions for station and availability data using a mocked database engine.
    """

    def setUp(self):
        """
        Prepare a sample JSON structure simulating a single station's data
        as returned by the JCDecaux API.
        """
        self.sample_data = json.dumps([
            {
                "number": 42,
                "address": "Station Road",
                "banking": True,
                "bike_stands": 25,
                "name": "Station 42",
                "status": "OPEN",
                "position": {"lat": 53.3, "lng": -6.2},
                "available_bikes": 10,
                "available_bike_stands": 15,
                "last_update": 1700000000000
            }
        ])

    def test_station_and_availability_insert(self):
        """
        Tests that the stations_to_db function:
        - Connects to the DB using a transactional engine.begin() context
        - Executes INSERT statements for both station and availability data
        - Calls .execute() at least twice (once for station, once for availability)
        """
        # Mock SQLAlchemy engine and connection
        mock_engine = MagicMock()
        mock_conn = MagicMock()

        # Patch the engine.begin() context manager to return our mock connection
        mock_engine.begin.return_value.__enter__.return_value = mock_conn

        # Simulate station record not already existing
        mock_conn.execute.return_value.scalar.return_value = 0
        mock_conn.execute.return_value.rowcount = 1

        # Call the target function
        JCDecauxAPI_to_DB.stations_to_db(self.sample_data, mock_engine)

        # Assertions
        self.assertTrue(mock_conn.execute.called, "Database execute method was not called.")
        self.assertGreaterEqual(
            mock_conn.execute.call_count, 2,
            "Expected at least 2 calls: one for station insert, one for availability insert."
        )


if __name__ == "__main__":
    unittest.main()
