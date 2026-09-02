# ORÁCULO — STACK PYTHON EJECUTABLE (fpppy-aligned)

> **Tipo:** documentación de infraestructura del esqueleto ejecutable.
> **Estado epistémico:** los hechos de instalación se etiquetan según ejecución real (`IMPLEMENTED` / `EXECUTED`); nada se declara `PROVEN` sin evidencia.

---

## 1. Qué es esto

Primera capa del esqueleto ejecutable del corpus AACC-PANDHARPUR: un entorno Python real que permite a ORÁCULO **ejecutar métodos de forecasting de las competencias M4/M5** en vez de describirlos. Alineación metodológica con **fpppy** (Forecasting: Principles and Practice — edición Python, OTexts 2026, <https://otexts.com/fpppy/> — `VERIFIED` en corpus).

| Componente | Estado real |
|---|---|
| Base Python 3.14.7 (`C:\Users\ACBM\AppData\Local\Python\pythoncore-3.14-64\python.exe`) | `OBSERVED` (py -0p + ejecución directa) |
| Venv `ORACLE-venv-314` (fuera de OneDrive) | `EXECUTED` (creado `python -m venv`) |
| statsmodels + scikit-learn + sktime + matplotlib instalados | `EXECUTED` cuando pip termine OK |
| `verify_stack.py` corriendo métodos reales | `EXECUTED` cuando el reporte exista |
| Auditoría independiente del stack | `NOT_AUDITED` (Four-Eyes pendiente) |

## 2. Diseño de ubicaciones (decisión deliberada)

- **Código y configuración** (requisitos, scripts, reports, ledger): en el workspace `C:\Users\ACBM\OneDrive\Documentos\DEEPSEEK\ORACLE` — es lo que se versiona y sincroniza.
- **Venv pesado** (miles de archivos en `Lib\site-packages`): en `C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314` — **fuera de OneDrive** a propósito: evita tormentas de sincronización, corrupción por archivos en uso y duplica el rendimiento.
- **Consecuencia:** el venv es específico de esta máquina. La reproducibilidad la garantizan `requirements.txt` + `requirements.lock.txt`, no el venv en sí.

## 3. Uso diario

```powershell
# Intérprete del venv (activación clásica opcional; se puede invocar directo):
C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314\Scripts\python.exe

# Desde el workspace:
cd C:\Users\ACBM\OneDrive\Documentos\DEEPSEEK\ORACLE
C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314\Scripts\python.exe verify_stack.py
```

`verify_stack.py` ejecuta **de verdad** (ajusta, pronostica, evalúa):

- **A · M4-style:** Theta (sktime), Seasonal Naive, ETS add/add/add (statsmodels), ARIMA(1,1,1)(0,1,1)₁₂ (statsmodels) — h=12, con MAE/RMSE/MASE/sMAPE sobre holdout.
- **B · M5-style:** reducción a regresor sklearn (`HistGradientBoostingRegressor`) vía `ReducedForecaster` de sktime con lags + variable promocional, benchmark contra Seasonal Naive estacional semanal.
- **C · Toolchain probabilística:** `CalibratedClassifierCV` isotónico (scikit-learn) + Brier Score — el circuito `P(EVENTO|EVIDENCIA)` del ORÁCULO.
- Escribe `verify_stack_report.md` (auditable) y devuelve exit code 0/1.

## 4. Mapa de métodos FPP3/fpppy → librería → competencia

| Método (FPP3/fpppy) | Librería | Competencia |
|---|---|---|
| Seasonal Naive / Naive | sktime (`NaiveForecaster`) | M4 baseline |
| Theta | sktime (`ThetaForecaster`) | M4 (top clásico) |
| ETS | statsmodels (`ETSModel`) | M4 / FPP ch. 7-8 |
| ARIMA/SARIMA | statsmodels (`ARIMA`) | M4 / FPP ch. 9 |
| STL decomposition | statsmodels | FPP ch. 3 |
| Reducción ML (lags + regresor) | sktime + scikit-learn | M5 (exógenas, jerárquico) |
| Combinación de pronósticos (Bates–Granger) | numpy/sktime ensemble | M4 top / FPP ch. 13 |
| Calibración probabilística | scikit-learn (`CalibratedClassifierCV`) | ORÁCULO `P(evento)` |
| Backtesting walk-forward | sktime (`evaluate`/`ExpandingWindowSplitter`) | M4/M5 evaluación |

## 5. Reproducir en otra máquina

```powershell
py -3.14 -m venv "C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314"
& "C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314\Scripts\python.exe" -m pip install -r requirements.txt
# fijar versiones exactas:
& "...\Scripts\python.exe" -m pip freeze > requirements.lock.txt
& "...\Scripts\python.exe" verify_stack.py
```

## 6. Limitaciones conocidas (transparencia)

- En sesiones DeepSeek Harness, la captura directa de stdout de procesos hijos se bloquea: los comandos largos se ejecutan vía `Start-Process` con redirección a archivo. El usuario, desde su propia consola, puede invocar Python sin restricción.
- La verificación usa series sintéticas deterministas: es smoke test de infraestructura. El benchmark sobre datos REALES M4 mensuales está en la sección 7.
- `_probe/` contiene artefactos temporales (logs); puede eliminarse.

## 7. Benchmark M4 real (walk-forward) — capa 2

```powershell
# 1) datos: descarga raw oficial (M4 monthly, ~92 MB → AppData, fuera de OneDrive)
#    y muestra determinista 60 series → data\m4_monthly_sample.csv
C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314\Scripts\python.exe fetch_m4_data.py

# 2) benchmark: walk-forward 2 folds expandentes, h=18 (horizonte M4 monthly)
C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314\Scripts\python.exe benchmark_m4.py
# → m4_benchmark_report.md + m4_benchmark_results.csv
```

**Resultados 2026-09-02 (60 series oficiales, h=18, OWA frente a SeasonalNaive):**

| Método | MASE | OWA |
|---|---|---|
| Theta (sktime) | 0.8367 | **0.7373** |
| ENSEMBLE media-simple | 0.8691 | 0.8054 |
| ARIMA(1,1,1)(0,1,1)₁₂ | 0.9194 | 0.8648 |
| ETS add/add/add | 0.9949 | 0.9670 |
| SeasonalNaive | 1.1264 | 1.0000 |

Lección registrada (APRENDIZAJE-001): con especificaciones fijas (sin auto-selección por serie), Theta domina y el ensemble de componentes débiles diluye; los hallazgos agregados de M4 no se transfieren sin calibrar componentes.

**Formato real del CSV M4** (`OBSERVED`): una fila por serie, `V1`=id (`M1`..`M48000`), `V2`..=observaciones (izquierda-alineadas, NaN al final).

## 8. Protocolo M4 AUTO — auto-selección por serie (capa 3a)

```powershell
C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314\Scripts\python.exe benchmark_m4_auto.py
# → m4_benchmark_auto_report.md + m4_benchmark_auto_results.csv
```

Añade AutoETS(`auto=True`), AutoARIMA (pmdarima) y **ENSEMBLE-AUTO** = media de
Theta+AutoETS+AutoARIMA. Misma muestra/folds que la sección 7 para comparación directa.

**Resultados 2026-09-02 (60 series, h=18):**

| Método | MASE | OWA |
|---|---|---|
| **ENSEMBLE-AUTO** | **0.8272** | **0.7221** |
| Theta | 0.8367 | 0.7373 |
| AutoETS | 0.8711 | 0.7601 |
| ENSEMBLE-FIXED (capa 2) | 0.8691 | 0.8054 |
| AutoARIMA | 0.9262 | 0.8367 |
| ARIMA-fijo | 0.9194 | 0.8648 |
| ETS-fijo | 0.9949 | 0.9670 |

Lectura: la auto-selección por serie mejora ETS (−12% MASE) y, con componentes de
calidad comparable, el ensemble gana al mejor individual (confirma APRENDIZAJE-001).
Matiz: AutoARIMA stepwise no superó al ARIMA fijo en MASE en esta muestra.

## 9. Pipeline M5-style jerárquico (capa 3b)

```powershell
C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-venv-314\Scripts\python.exe benchmark_m5h.py
# → m5_hierarchical_report.md
```

Jerarquía de demostración (24 series reales M4 → 4 grupos → total), Theta sp=12 por
nodo, holdout final h=6: **DIRECT** vs **BOTTOM-UP** vs **WLS-DIAG** (reconciliación
con pesos diagonales; proxy honesto del MinT — el MinT real requiere la covarianza
de errores de pronóstico). Coherencia de la proyección verificada (~1e-11).

**Resultado 2026-09-02 (holdout final):** DIRECT MASE 2.570 < WLS-DIAG 2.570 <
BOTTOM-UP 3.133 — en esta ventana volátil el pronóstico directo sobre el agregado
ganó; la reconciliación WLS-DIAG quedó ≈ directa por la disparidad de escalas.
Dataset oficial M5 (Walmart, Kaggle): **bloqueo documentado** — requiere credenciales;
la maquinaria (jerarquía+reconciliación) está verificada y lista para datos reales M5.
