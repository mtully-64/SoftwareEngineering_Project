
# Testing Suite Summary

This document provides a combined overview of the test suite implemented for the Dublin Bike Sharing System, covering the backend Flask application, database ingestion logic, and machine learning predictions.

---

## Overview

The project includes a unified test suite that brings together:
- **Application-level tests** for Flask routes, APIs, and authentication
- **Local SQL database modules** for station, availability, and weather records
- **Machine Learning model tests** for prediction accuracy and model loading

The test suite is organized under the `tests/` directory, with each module structured to reflect its purpose. Tests are implemented using Python's built-in `unittest` framework, with extensive use of mocking (`unittest.mock`) to isolate functionality and avoid dependence on live services.

---

## Test Structure

```
tests/
├── app/
│   └── test_app.py                         # Flask app and API endpoint tests
├── database/
│   ├── test_jcdecaux_db.py                # Local SQL station + availability table creation test
│   ├── test_openweather_db.py             # Local SQL weather + forecast schema test
│   ├── test_jcdecauxapi_to_db.py          # JCDecaux station + availability insertion logic
│   ├── test_openweatherapi_to_db.py       # Weather and forecast ingestion into SQL
│   ├── test_jcdecauxapi_to_file.py        # 12 hour file scrapping for JCDecaux data
│   └── test_openweatherapi_to_file.py     # 12 hour file scrapping for weather data
├── machine_learning/
│   └── test_prediction.py                 # ML model loading and prediction tests
└── test_suite.py                          # Aggregates all tests into a unified suite

```
---

## Included Test Types

### Flask App Tests
- Tests core API endpoints such as `/api/bike_stations`, `/api/weather`, `/login`, and `/dashboard`
- Verifies token-based route protection using mocked Firebase credentials
- Includes both positive and negative test cases for session handling and redirection

### Local SQL Database Logic
- `test_jcdecaux_db.py`: Validates SQL schema creation for `station` and `availability`
- `test_jcdecauxapi_to_db.py`: Simulates inserting live station data (mocked API + DB)
- `test_openweatherapi_to_db.py`: Inserts current and forecast weather based on station coordinates
- `*_to_file.py`: Tests fallback behavior for 12hr local scraping

### Machine Learning Tests
- Loads the `Dubike_random_forest_model.joblib` prediction model
- Ensures numeric predictions are returned with valid features
- Verifies rejection of malformed or incomplete input data
- All test paths simulate realistic model interactions used in the live backend

---

## Running the Suite

To run all tests from the project root:

```bash
python -m tests.test_suite
```

This will execute:
- All Flask app tests
- Database schema and data-insertion tests (local SQL)
- Machine learning prediction tests
- 12 hour API scraping for JSON file output

---

## Coverage

Coverage is tracked using `coverage.py`:

```bash
coverage run -m unittest tests.test_suite
coverage report -m
```

Example output:

```
Name                                        Stmts   Miss  Cover
---------------------------------------------------------------
app/app.py                                    112     18    84%
tests/app/test_app.py                          75      0   100%
tests/database/test_jcdecaux_db.py             33      1    97%
tests/database/test_jcdecauxapi_to_db.py       41      0   100%
tests/database/test_jcdecauxapi_to_file.py     35      0   100%
tests/database/test_openweatherapi_to_db.py    38      2    95%
tests/database/test_openweatherapi_to_file.py  36      0   100%
tests/machine_learning/test_prediction.py      29      0   100%
tests/test_suite.py                            14      0   100%
---------------------------------------------------------------
TOTAL                                         413     21    92%

```

---

## Conclusion

The test suite achieves 92% line coverage and thoroughly validates the system across its key technical domains. With database mocking, offline fallback logic, and predictive analytics verification, this setup ensures maintainability, test isolation, and production-aligned behavior for real-time operations in the Dublin Bike Sharing System.
