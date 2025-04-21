
# Database Testing – JCDecaux & OpenWeather Integration

This document details the testing efforts specifically focused on the **database modules** inside the `app/database/` directory of the project.

Due to the suspension of the Amazon RDS instance, the project now uses both local file outputs to simulate and validate data ingestion logic, as well as a local SQL database.

All tests are executed using mocked database connections, avoiding the need for a live SQL instance while preserving coverage and correctness of logic.
---

## Test Types Performed

The following tests were designed to validate the core functionality of the database pipeline for both JCDecaux and OpenWeather integrations:

- **Mocking**:
  - `mock_open()` to intercept and verify local file writing
  - `MagicMock()` to simulate SQL connection calls
  - `patch()` to fake external API responses and keys

- **Assertions**:
  - `mock_conn.execute.call_count` ensures that SQL statements are triggered
  - `scalar.return_value` is used to simulate pre-insertion checks (e.g., duplicates)
  - `write.call_args_list` confirms file output matches expectations

---

## Targeted Modules

| Module                      | Description                                                  |
|----------------------------|--------------------------------------------------------------|
| `JCDecaux_DB.py`           | Defines SQL schema for stations and availability             |
| `OpenWeather_DB.py`        | Defines SQL schema for weather and forecast data             |
| `JCDecauxAPI_to_DB.py`     | Main parser and DB writer for station & availability records |
| `OpenWeatherAPI_to_DB.py`  | Fetches and writes current & forecast weather data           |

---

## Test Files & Purpose

Each of the following tests is stored in `/tests/database/` and is run independently from a live DB, using mocks:

| Test File                         | Purpose                                                                 |
|----------------------------------|-------------------------------------------------------------------------|
| `test_jcdecaux_db.py`            | Tests that station and availability table SQL creation can be invoked |
| `test_jcdecauxapi_to_db.py`      | Validates station insertion and availability insertions from JSON     |
| `test_jcdecauxapi_to_file.py`    | Tests fallback file output if DB engine is unavailable  (necessary for 12hr local file scraping)               |
| `test_openweather_db.py`         | Verifies table creation logic for current_weather and daily_forecast   |
| `test_openweatherapi_to_db.py`   | Tests correct parsing of API responses and their insertion into tables |
| `test_openweatherapi_to_file.py` | Simulates offline behavior and confirms record generation     (necessary for 12hr local file scraping)         |

Each of these test files mocks the SQLAlchemy `engine.begin()` or database execution logic to keep tests fast and decoupled from infrastructure.

---

## How to Run the Tests

To run all database-related unit tests from the project root:

```bash
python -m unittest tests/database/test_jcdecaux_db.py
python -m unittest tests/database/test_jcdecauxapi_to_db.py
python -m unittest tests/database/test_jcdecauxapi_to_file.py
python -m unittest tests/database/test_openweather_db.py
python -m unittest tests/database/test_openweatherapi_to_db.py
python -m unittest tests/database/test_openweatherapi_to_file.py

---

## Conclusion

The adapted database testing approach guarantees:
- The parsing logic is thoroughly validated
- Integration with local storage works in place of a live DB
- No loss of test coverage despite cloud service suspension

These tests are lightweight, mock-driven, and ready for continuous integration or future upgrade.
