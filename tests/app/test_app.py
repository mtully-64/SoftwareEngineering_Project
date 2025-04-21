import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add app directory to the path to allow importing app.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app')))
from app import app  # Import the Flask app instance


class TestFlaskApp(unittest.TestCase):
    """
    Unit test suite for the Flask backend.
    Covers:
    - Routing and redirects
    - Session management
    - API responses (including mocks for data-fetching functions)
    """

    def setUp(self):
        """
        Set up a test client before each test.
        """
        self.app = app.test_client()
        self.app.testing = True

    # ---------- ROUTING TESTS ----------

    def test_home_redirects_to_login(self):
        """
        Unauthenticated access to "/" should redirect to "/login".
        """
        response = self.app.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_login_page_renders(self):
        """
        Test that the login page renders successfully.
        """
        response = self.app.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_signup_page_renders(self):
        """
        Test that the signup page renders successfully.
        """
        response = self.app.get("/signup")
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_to_login(self):
        """
        After logout, the user should be redirected to login page.
        """
        with self.app.session_transaction() as sess:
            sess["user"] = "test-user"
        response = self.app.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"login", response.data.lower())

    def test_dashboard_redirects_if_not_logged_in(self):
        """
        Unauthenticated access to /dashboard should redirect to login.
        """
        response = self.app.get("/dashboard", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"login", response.data.lower())

    # ---------- DASHBOARD TESTS WITH MOCKED DATA ----------

    @patch("app.fetch_bike_stations")
    def test_dashboard_renders_when_logged_in(self, mock_fetch):
        """
        If logged in, dashboard should load with mock station data.
        """
        mock_fetch.return_value = [{
            "number": 1, "name": "Station A", "position": {"lat": 53.3, "lng": -6.2}
        }]
        with self.app.session_transaction() as sess:
            sess["user"] = "test-user"
            sess["first_name"] = "Test"
        response = self.app.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dublin Bikes", response.data)

    # ---------- API ENDPOINT TESTS ----------

    @patch("app.fetch_bike_stations")
    def test_api_bike_stations(self, mock_fetch):
        """
        Test /api/bike_stations returns mocked station data correctly.
        """
        mock_fetch.return_value = [{"number": 1, "name": "Station A"}]
        response = self.app.get("/api/bike_stations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [{"number": 1, "name": "Station A"}])

    @patch("app.fetch_weather_data")
    def test_api_weather(self, mock_fetch_weather):
        """
        Test /api/weather with mock weather data.
        """
        mock_fetch_weather.return_value = {
            "main": {"temp": 15},
            "wind": {"speed": 5},
            "weather": [{"main": "Clear"}]
        }
        response = self.app.get("/api/weather?lat=53.3&lon=-6.2")
        self.assertEqual(response.status_code, 200)
        self.assertIn("main", response.get_json())

    def test_api_google_maps_key(self):
        """
        Test /api/google-maps-key returns a JSON key.
        """
        response = self.app.get("/api/google-maps-key")
        self.assertEqual(response.status_code, 200)
        self.assertIn("apiKey", response.get_json())

    # ---------- AUTH & LOGIN TESTS ----------

    @patch("app.auth.verify_id_token")
    def test_verify_login_success(self, mock_verify):
        """
        Simulate successful Firebase login verification.
        """
        mock_verify.return_value = {"uid": "test-user"}
        response = self.app.post("/verify_login", json={"idToken": "fake-token"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["success"], True)

    def test_verify_login_missing_token(self):
        """
        Verify login fails if no ID token is provided.
        """
        response = self.app.post("/verify_login", json={})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["success"], False)

    # ---------- ERROR HANDLING TESTS ----------

    def test_api_history_data_missing_param(self):
        """
        Test /api/history_data without station_id returns 400 error.
        """
        response = self.app.get("/api/history_data")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing station_id", response.get_data(as_text=True))

    def test_api_history_dates_missing_param(self):
        """
        Test /api/history_dates without station_id returns 400 error.
        """
        response = self.app.get("/api/history_dates")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing station_id", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
