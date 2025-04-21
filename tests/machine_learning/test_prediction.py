import unittest
import os
import pandas as pd
import numpy as np
import joblib

class TestMLPrediction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Load the ML model from the main /app directory.
        """
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'Dubike_random_forest_model.joblib')
        cls.model = joblib.load(model_path)

    def test_model_loads(self):
        """Check that the model loads correctly."""
        self.assertIsNotNone(self.model)

    def test_prediction_output(self):
        """
        Feed the model dummy data and check that the output is numeric.
        Features: station_id, max_temp, min_temp, humidity, pressure, hour, day
        """
        test_input = pd.DataFrame([[
            42,       # station_id
            14.5,     # max_temp
            9.3,      # min_temp
            75,       # humidity
            1013,     # pressure
            9,        # hour of day
            2         # day of week (Tuesday)
        ]], columns=[
            "station_id", "max_temperature", "min_temperature", "humidity", "pressure", "hour", "day"
        ])

        prediction = self.model.predict(test_input)
        self.assertTrue(isinstance(prediction[0], (float, np.floating, int)))

    def test_invalid_input_shape(self):
        """Test model behavior when given incorrect input shape."""
        with self.assertRaises(ValueError):
            self.model.predict([[1, 2, 3]])  # Too few features

if __name__ == "__main__":
    unittest.main(verbosity=2)
