import sys
import os
import unittest
from unittest.mock import mock_open, patch

# Add the database module to the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'database')))

from JCDecauxAPI_to_DB import stations_to_db  # Import the target function


class TestJCDecauxToFile(unittest.TestCase):
    """
    Unit test for JCDecauxAPI_to_DB.stations_to_db when no database engine is provided.
    Verifies that the function falls back to writing parsed station data to a local file.
    """

    def setUp(self):
        """
        Setup a sample JSON input string representing a valid JCDecaux API response.
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

    @patch("builtins.open", new_callable=mock_open)
    def test_writes_data_to_file(self, mock_file):
        """
        Test that verifies:
        - open() is called when engine is None
        - the file write operation occurs
        - the output contains recognizable station information
        """
        mock_engine = None  # Simulate a missing database engine
        stations_to_db(self.sample_data, mock_engine)

        # Assert that the file was opened (write mode)
        mock_file.assert_called()

        # Retrieve the mock file handle and assert that write was called
        handle = mock_file()
        self.assertTrue(handle.write.called, "Expected write to be called on file handle.")

        # Validate that expected station content appears in the written output
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn("Station 42", written_data, "Expected station name not found in written output.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
