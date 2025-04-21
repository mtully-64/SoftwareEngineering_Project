
import unittest

# Import the test case for the Flask app
from tests.app.test_app import TestFlaskApp

# Local SQL database tests (we removed the AWS RDS ones as they were suspended)
from tests.database.test_jcdecaux_db import TestJCDecauxDB
from tests.database.test_jcdecauxapi_to_db import TestJCDecauxAPIToDB
from tests.database.test_openweatherapi_to_db import TestOpenWeatherAPIToDB
from tests.database.test_openweather_db import TestOpenWeatherDB

# File-based mock tests (checking the API functionality for when we scraped for 12 hours)
from tests.database.test_jcdecauxapi_to_file import TestJCDecauxToFile
from tests.database.test_openweatherapi_to_file import TestOpenWeatherToFile

# Machine learning prediction test
from tests.machine_learning.test_prediction import TestMLPrediction

def suite():
    """
    Creates a test suite that aggregates individual test cases.
    """
    test_suite = unittest.TestSuite()

    # Flask app routes and authentication
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFlaskApp))

    # JCDecaux DB logic
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestJCDecauxDB))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestJCDecauxAPIToDB))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestJCDecauxToFile))

    # OpenWeather DB integration logic
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestOpenWeatherAPIToDB))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestOpenWeatherToFile))

    # Machine Learning prediction test
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMLPrediction))

    return test_suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
