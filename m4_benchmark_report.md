# ORÁCULO — Benchmark walk-forward M4 (datos reales, muestra oficial)

- Fecha: 2026-09-02T08:11:07
- Fuente: Mcompetitions/M4-methods (Monthly-train.csv), muestra determinista
- Series evaluadas: 60 · folds por serie: 2 · h=18
- Filas de evaluación: 600 · errores de ajuste: {'SeasonalNaive': 0, 'Theta': 0, 'ETS': 0, 'ARIMA': 0, 'ENSEMBLE': 0}

| método | MASE medio | sMAPE medio | OWA (vs SNaive) |
|---|---|---|---|
| Theta | 0.8367 | 12.05% | 0.7373 |
| ENSEMBLE | 0.8691 | 13.82% | 0.8054 |
| ARIMA | 0.9194 | 15.04% | 0.8648 |
| ETS | 0.9949 | 17.30% | 0.9670 |
| SeasonalNaive | 1.1264 | 16.46% | 1.0000 |

**OJO:** benchmark de infraestructura sobre datos ya observados (evaluación de métodos M4-style); no es un pronóstico de eventos futuros ni entrada de calibración del ledger.
