# ORACULO - Validacion OOS vs test oficial M4 (capa 4)

- Fecha: 2026-09-02T10:17:20
- Metodo: ENSEMBLE-AUTO (Theta+AutoETS+AutoARIMA) + intervalos gaussianos empiricos (sigma_pooled*sqrt(h))
- Series: 60 (test oficial jamas usado en desarrollo) x h=18 = 1080 puntos OOS

| metrica | valor |
|---|---|
| MASE medio OOS | 0.8002 |
| sMAPE medio OOS | 11.15% |
| MAE medio OOS | 496.853 |
| cobertura nominal 80% (P10-P90) | 100.0% (1080/1080) |
| series con MASE>1 (peor que naive) | 26.7% |

Notas epistemicas: intervalos basados en sigma_pooled (familia ETS/ARIMA/naive) con aproximacion iid sqrt(h) - la cobertura empirica mide su calibracion real. Si coverage >> 80%, los intervalos son conservadores (sobre-anchos); si < 80%, subestiman incertidumbre.
