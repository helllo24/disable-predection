| Model Calibration Status | Brier Score | Calibration Slope | Calibration Intercept | Decision Threshold | Calibration Method |
| --- | --- | --- | --- | --- | --- |
| Uncalibrated XGBoost Model | 0.0033 | 0.9067 | 0.0333 | 0.5 | None (Raw Probability Outputs) |
| Isotonic Calibrated XGBoost Model | 0.0034 | 0.9822 | -0.0321 | 0.3 | Isotonic Regression (Fit on Validation Split) |