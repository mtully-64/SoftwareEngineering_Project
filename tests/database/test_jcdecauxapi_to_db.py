import sys
import os
import unittest
from unittest.mock import MagicMock

# Extend the import path to load modules from app/database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'database')))

# Import the JCDecaux insertion logic
from JCDecauxAPI_to_DB import stations_to_db

class TestJCDecauxAPIToDB(unittest.TestCase):
    """
    Unit tests for JCDecauxAPI_to_DB module.
    Verifies that station and availability data from JCDecaux API
    is correctly parsed and inserted into the local SQL database using mocked engine.
    """

    def setUp(self):
        """
        Prepare a valid sample JSON string simulating a JCDecaux station API response.
        """
        self.sample_data = '''
        [
            {
                "number": 42,
                "address": "Test Street",
                "banking": true,
                "bike_stands": 20,
                "name": "Station 42",
                "status": "OPEN",
                "position": {"lat": 53.3, "lng": -6.2},
                "available_bikes": 10,
                "available_bike_stands": 10,
                "last_update": 1700000000000
            }
        ]
        '''

    def test_station_and_availability_insert(self):
        """
        Test that:
        - The station is inserted if it does not already exist (mocked check returns 0)
        - Availability data is inserted unconditionally
        - .execute() is called at least twice (once per insert target)
        """
        # Mock the SQLAlchemy engine and DB connection context
        mock_engine = MagicMock()
        mock_conn = MagicMock()

        # Simulate the transactional context manager behavior
        mock_engine.begin.return_value.__enter__.return_value = mock_conn

        # Simulate DB check response: station does not exist
        mock_conn.execute.return_value.scalar.return_value = 0
        mock_conn.execute.return_value.rowcount = 1  # simulate successful insert

        # Execute the function under test
        stations_to_db(self.sample_data, mock_engine)

        # Assertions
        self.assertTrue(mock_conn.execute.called, "Expected execute() to be called at least once.")
        self.assertGreaterEqual(
            mock_conn.execute.call_count, 2,
            "Expected at least two calls to execute() for station and availability inserts."
        )

if __name__ == "__main__":
    unittest.main()
