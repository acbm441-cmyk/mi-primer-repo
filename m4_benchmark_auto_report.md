# ORÁCULO — Benchmark M4 protocolo AUTO (auto-selección por serie)

- Fecha: 2026-09-02T08:51:12
- Muestra: 60 series M4 mensuales reales · folds=2 · h=18
- AutoARIMA disponible: True
- Errores de ajuste: {'SeasonalNaive': 0, 'Theta': 0, 'ETS-fixed': 0, 'ARIMA-fixed': 0, 'AutoARIMA': 1, 'AutoETS': 0, 'ENSEMBLE-AUTO': 0, 'ENSEMBLE-FIXED': 0}

| método | MASE medio | sMAPE medio | OWA |
|---|---|---|---|
| ENSEMBLE-AUTO | 0.8272 | 11.69% | 0.7221 |
| Theta | 0.8367 | 12.05% | 0.7373 |
| AutoETS | 0.8711 | 12.29% | 0.7601 |
| ENSEMBLE-FIXED | 0.8691 | 13.82% | 0.8054 |
| AutoARIMA | 0.9262 | 14.01% | 0.8367 |
| ARIMA-fixed | 0.9194 | 15.04% | 0.8648 |
| ETS-fixed | 0.9949 | 17.30% | 0.9670 |
| SeasonalNaive | 1.1264 | 16.46% | 1.0000 |
