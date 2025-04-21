
# Flask App Testing Report

This document outlines the testing strategy applied to the Flask web application defined in `app/app.py`, which serves as the backend for the Dublin Bikes web platform. These tests focus on routing logic, API endpoints, login/logout flow, and frontend integration.

---

## Test Types Performed

The following test types were conducted:

- Unit testing using `unittest` and Flask's `test_client`
- Mocking for Firebase authentication and external API calls
- Session handling and access control
- Contract testing for JSON API endpoints used by the frontend

---


## List of Tests and Expected Outcomes

| Test Name                            | Description                                                             | Expected Outcome                                 |
|-------------------------------------|-------------------------------------------------------------------------|--------------------------------------------------|
| test_home_redirects_to_login        | Accessing `/` redirects to login when not authenticated                 | 302 redirect to `/login`                         |
| test_login_page_renders             | Loads the login page                                                    | Status code 200                                  |
| test_signup_page_renders            | Loads the signup page                                                   | Status code 200                                  |
| test_logout_redirects_to_login      | Logout clears session and redirects to login                            | Redirect with login page in response             |
| test_dashboard_redirects_if_not_logged_in | Accessing `/dashboard` without login redirects to `/login`          | Redirect with login page in response             |
| test_dashboard_renders_when_logged_in | Authenticated user can access dashboard                                | Status code 200 with page content                |
| test_api_bike_stations              | Bike station API returns valid JSON                                     | Status code 200 with station data                |
| test_api_weather                    | Weather API returns structured weather JSON                             | Status code 200 with temperature, wind, etc.     |
| test_api_google_maps_key           | Google Maps API key is returned                                         | Status code 200 with `apiKey` in JSON            |
| test_verify_login_success           | Firebase ID token verification works when mocked                        | Status code 200 and `success: true`              |
| test_verify_login_missing_token     | Login fails if no token is provided                                     | Status code 401 and `success: false`             |
| test_api_history_data_missing_param | Missing required `station_id` returns error                             | Status code 400 and error message in response    |
| test_api_history_dates_missing_param| Same as above for history dates                                         | Status code 400 and error message in response    |

---

## Test Coverage and Results

- All routes and APIs tested passed successfully
- Firebase interaction was mocked to avoid real network calls
- JSON structure of API responses validated where applicable
- Test coverage includes all backend endpoints used by the frontend

To run the tests:

```bash
python tests/app/test_app.py
```

---

## Usability Testing Outcomes

Informal usability testing was performed with three users who interacted with the login and dashboard views (family members).

### Summary of Feedback:

- The login flow was intuitive, and redirection worked as expected
- Some confusion occurred around what happens post-logout (no visual indicator)
- Frontend properly reflected backend state (e.g., availability, weather)
- Minor suggestion to add clearer error messages on login failure

> Based on feedback, visual cues were added after logout, and error messages were improved in Sprint 3 (this is why there is a large change to our front end in the commit history!).

---

## Conclusion

The application testing strategy focused on covering meaningful scenarios that impact both security and user experience. It validates that:

- API endpoints are reachable and reliable
- Authentication logic works and is secure
- The frontend can communicate with the backend without issue

These tests form a stable foundation for ensuring backend quality and frontend functionality.
