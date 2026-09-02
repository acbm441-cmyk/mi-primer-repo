# ORÁCULO — verificación del stack (reporte generado)

- Fecha: 2026-09-02T08:04:23
- Python: 3.14.7 · ejecutable: C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314\Scripts\python.exe
- Versiones: {"python": "3.14.7", "numpy": "2.4.6", "pandas": "2.3.3", "scipy": "1.18.1", "statsmodels": "0.15.0", "scikit-learn": "1.7.2", "sktime": "1.1.0", "matplotlib": "3.11.1"}

| método | MAE | RMSE | MASE | sMAPE |
|---|---|---|---|---|
| Theta (sktime) | 3.096 | 3.607 | 0.727 | 3.79% |
| SeasonalNaive sp12 (sktime) | 4.270 | 4.525 | 1.003 | 5.47% |
| ETS add/add/add (statsmodels) | 1.010 | 1.275 | 0.237 | 1.24% |
| ARIMA(1,1,1)(0,1,1)12 (statsmodels) | 0.995 | 1.279 | 0.234 | 1.23% |
| Reduction GBR lag8+promo (sktime+sklearn) | 2.764 | 3.419 | 0.722 | 7.36% |
| SeasonalNaive sp52 (benchmark) | 3.049 | 3.813 | 0.797 | 8.62% |
| CalibratedClassifierCV isotonic | Brier=0.2085 |  |  |  |

**Casos fallidos: 0**
