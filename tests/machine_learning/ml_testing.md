
# Machine Learning Testing Report

This document outlines the testing strategy applied to the machine learning prediction model used in the Dublin Bikes web platform. The model is responsible for predicting bike availability using environmental and temporal features such as weather conditions, hour of day, and station ID.

---

## Test Types Performed

The following test types were conducted:

- Unit testing using `unittest`
- Model loading from `.joblib` format using `joblib`
- Input validation and output format testing
- Error handling for incorrect input shape

---

## List of Tests and Expected Outcomes

| Test Name                | Description                                                           | Expected Outcome                                       |
|-------------------------|-----------------------------------------------------------------------|--------------------------------------------------------|
| test_model_loads        | Ensure the Random Forest model loads successfully from file           | Model is loaded and not `None`                         |
| test_prediction_output  | Model receives correct input and returns a valid numeric prediction   | A float or int value is returned                       |
| test_invalid_input_shape| Model raises `ValueError` when given an input with wrong dimensions   | Exception is raised as expected                        |

---

## Test Coverage and Results

- The test file `test_prediction.py` under `tests/machine learning/` covers all critical paths
- Inputs were mocked to replicate production model calls in `/app/app.py`
- Tests ensured robustness of the prediction logic before API integration

To run the tests:

```bash
python -m unittest tests.machine\ learning.test_prediction
```

---

## Usability Testing Outcomes

No direct frontend usability testing was conducted for the machine learning model, as its function is backend-focused. However, the output of predictions was manually verified through the dashboard's prediction features.

### Summary of Model Validation:

- Dummy data covering all required input features was used
- Predictions were visually confirmed via the frontend when API integration was active
- Model behavior on edge input values was assessed

---

## Conclusion

The machine learning tests ensure the integrity of the prediction pipeline, which is a key feature of the web application. The tests confirm:

- The model loads and executes predictably
- Input formatting is enforced
- Failures are handled gracefully

These tests help maintain confidence in future forecasting functionality as part of the system’s decision support features.
