# 🧠 ORÁCULO — MEMORIA PERSISTENTE DEL ECOSISTEMA AACC-PANDHARPUR

> **Tipo de archivo:** Memoria de contexto persistente del agente ORÁCULO.
> **Ruta:** `C:\Users\ACBM\OneDrive\Documentos\DEEPSEEK\ORACLE\oracle_memory.md`
> **Versión:** 1.0 · **Creado:** 2026-09-02 · **Modelo:** deepseek-v4-flash
> **Regla de oro del archivo:** solo contiene lo que puede sostenerse con evidencia. Los datos pendientes se marcan `PENDING_CONFIRMATION` y NUNCA se rellenan con suposiciones (`ASSUMED → VERIFIED` prohibido).
> **Jerarquía epistémica aplicada:** `OBSERVED` · `VERIFIED` · `SUPPORTED` · `INFERRED` · `ASSUMED` · `SPECULATIVE` · `UNKNOWN`

---

## 1. IDENTIDAD Y MISIÓN DEL AGENTE

**Fuente:** prompt maestro ORÁCULO v1.0 (AACC-PANDHARPUR) — `VERIFIED`.

- **Nombre:** ORÁCULO.
- **Naturaleza:** agente de inteligencia predictiva e inferencia estadística del ecosistema AACC-PANDHARPUR. No es un adivino; no conoce el futuro con certeza.
- **Misión fundamental:** transformar evidencia verificable en pronósticos probabilísticos calibrados, escenarios futuros, distribuciones de resultados y recomendaciones de decisión explícitamente condicionadas por incertidumbre.
- **Objetivo formal:** aproximar `P(EVENTO FUTURO | EVIDENCIA DISPONIBLE)` mediante métodos reproducibles, auditables y estadísticamente defendibles.
- **Dominios de operación:** mercados, negocios, tecnología, operaciones, proyectos, IA, software, seguridad, demanda, logística, estrategia, escenarios geopolíticos, forecasting científico, reliability engineering, cronogramas, riesgos.

**Estado:** `ORACLE_CORE = ACTIVE` · `EPISTEMIC_HUMILITY = ENFORCED` · `FALSE_CERTAINTY = FORBIDDEN` · `CALIBRATION = REQUIRED` · `AUDITABILITY = REQUIRED` — `VERIFIED`.

---

## 2. GOBERNANZA DEL ECOSISTEMA

**Fuente:** prompt maestro ORÁCULO v1.0 — `VERIFIED` (definición declarada; su operación real en la práctica está `PENDING_CONFIRMATION`).

| Rol | Designación | Función |
|---|---|---|
| Autoridad humana | `HITL-00` | Autoridad humana final; el pronóstico de ORÁCULO no sustituye su autoridad. |
| Supervisor operativo | `AG-01` | Supervisión operativa del ecosistema. |
| Inteligencia probabilística | `ORÁCULO` | Agente de pronóstico, análisis y calibración. |

**Principios de gobernanza aplicables:**

- Separación estricta de estados: `DECLARED` ≠ `DOCUMENTED` ≠ `IMPLEMENTED` ≠ `EXECUTED` ≠ `PROVEN` ≠ `AUDITED` ≠ `CERTIFIED`. La documentación declarativa NUNCA es evidencia automática de ejecución real.
- ORÁCULO no autocertifica trabajos que requieran auditor independiente (principio Four-Eyes para predicciones de alta consecuencia).
- Salida estándar: `FORECAST`, no `CERTIFICATE`.

---

## 3. ESTADO DEL ECOSISTEMA AACC-PANDHARPUR — `PENDING_CONFIRMATION`

> ⚠️ Bloque reservado. ORÁCULO NO tiene todavía información verificada sobre estos puntos.
> Proporcionar datos reales antes de poblar. Nada de esto debe rellenarse por inferencia.

| Campo | Estado | Valor cuando se confirme |
|---|---|---|
| ¿Qué es AACC-PANDHARPUR? (proyecto/organización/misión) | `UNKNOWN` | — |
| Objetivos declarados | `UNKNOWN` | — |
| Hitos y cronograma | `UNKNOWN` | — |
| Componentes, dominios o líneas de trabajo | `UNKNOWN` | — |
| Miembros y roles operativos reales | `UNKNOWN` | — |
| Evidencia de ejecución (documentos, logs, entregables) | `UNKNOWN` | — |
| Métricas objetivo del ecosistema | `UNKNOWN` | — |

**Regla:** cuando se incorpore información, cada dato llevará su etiqueta epistémica y su fuente. Los datos que provengan solo de declaraciones se marcarán `DECLARED` hasta que exista evidencia.

---

## 4. INVENTARIO DE HECHOS ESTABLECIDOS (`VERIFIED` — comprobados el 2026-09-02)

| # | Hecho | Estado | Evidencia |
|---|---|---|---|
| F1 | El workspace de trabajo es `C:\Users\ACBM\OneDrive\Documentos\DEEPSEEK\ORACLE` | `OBSERVED` | Comprobación de directorio 2026-09-02 |
| F2 | El modelo activo es deepseek-v4-flash | `VERIFIED` | Configuración de sesión |
| F3 | Existe el ledger persistente `oracle_forecasts.jsonl` en el workspace | `OBSERVED` | `oracle_status` 2026-09-02 |
| F4 | El ledger contiene 0 pronósticos registrados (0 abiertos, 0 resueltos) | `OBSERVED` | `oracle_status` 2026-09-02 |
| F5 | No existe aún calibración empírica (n_resolved = 0) → NO se reportan métricas de calibración | `OBSERVED` | `oracle_status` 2026-09-02 |
| F6 | Se creó `oracle_memory.md` (este archivo) | `VERIFIED` | Escritura 2026-09-02 |
| F7 | Se creó `oracle_learnings.md` | `VERIFIED` | Escritura 2026-09-02 |
| F8 | Se creó el venv `ORACLE-venv-314` en `C:\Users\ACBM\AppData\Local\DEEPSEEK` (fuera de OneDrive, decisión deliberada anti-tormenta-de-sincronización) sobre base Python 3.14.7 | `OBSERVED` | `python -m venv` 2026-09-02 (exit OK) |
| F9 | Stack fpppy-aligned instalado en el venv con wheels cp314 reales: statsmodels 0.15.0 · scikit-learn 1.7.2 · sktime 1.1.0 · matplotlib 3.11.1 (numpy 2.4.6, pandas 2.3.3, scipy 1.18.1) | `OBSERVED` | `pip install` 2026-09-02, `Successfully installed` |
| F10 | `verify_stack.py` ejecuta de verdad métodos M4/M5-style: 7/7 casos PASS (Theta, SeasonalNaive sp12, ETS, ARIMA, reducción GBR con exógena, naive sp52, calibración isotónica con Brier) | `OBSERVED` | `verify_stack_report.md` 2026-09-02T08:04:23, exit 0 |
| F11 | Limitación documentada del entorno: `HistGradientBoostingRegressor` y backends joblib con threads/subprocesos NO ejecutan en procesos lanzados desde el sandbox DSH (creación de pipes bloqueada → WinError 5); `GradientBoostingRegressor` clásico y el resto del stack SÍ | `OBSERVED` | Sondas de ejecución `_probe` p3/p4, 2026-09-02 |
| F12 | `requirements.lock.txt` congela 27 dependencias exactas; `requirements.txt` lista las 4 de nivel superior | `OBSERVED` | `pip freeze` 2026-09-02 |
| F13 | Raw M4 monthly oficial descargado (91.7 MB, 48.000 series, longitud media 216, máx 2794) en `AppData\Local\DEEPSEEK\ORACLE-data\M4` (fuera de OneDrive); muestra determinista de 60 series (n>=48) en `data/m4_monthly_sample.csv` | `OBSERVED` | `fetch_m4_data.py` 2026-09-02 |
| F14 | Formato REAL del CSV M4 de entrenamiento: una FILA por serie (`V1` = id "M1".."M48000", `V2`.. = observaciones, relleno NaN al final). El supuesto inicial columnas-por-serie fue erróneo y la primera muestra generada se descartó | `OBSERVED` | Inspección directa del archivo 2026-09-02 |
| F15 | Benchmark walk-forward ejecutado sobre datos M4 reales (60 series × 2 folds, h=18, 600 filas, 69 s): ranking OWA Theta 0.7373 < ENSEMBLE 0.8054 < ARIMA 0.8648 < ETS 0.9670 < SeasonalNaive 1.0; todos los métodos MASE<1 y victoria vs naive en 67–77% de series | `OBSERVED` | `m4_benchmark_report.md` + `m4_benchmark_results.csv` 2026-09-02 |
| F16 | Primeros registros RESUELTOS del ledger (ejercicio pre-registrado, etiquetado, no eventos reales): ORACLE-2026-0001 P=0.70 → outcome 0 (Brier 0.4900); ORACLE-2026-0002 P=0.55 → outcome 1 (Brier 0.2025). Brier medio real 0.3463 con n=2 — NO se reporta calibración con n<30 | `OBSERVED` | `oracle_status` 2026-09-02 |
| F17 | Benchmark protocolo AUTO ejecutado (60 series × 2 folds × 8 métodos, 959 filas, 35.4 min, 1 fallo AutoARIMA/120 folds): ranking OWA ENSEMBLE-AUTO 0.7221 < Theta 0.7373 < AutoETS 0.7601 < ENSEMBLE-FIXED 0.8054 < AutoARIMA 0.8367 < ARIMA-fijo 0.8648 < ETS-fijo 0.9670 < SNaive 1.0 | `OBSERVED` | `m4_benchmark_auto_report.md` + `m4_benchmark_auto_results.csv` 2026-09-02 |
| F18 | AutoETS(auto) MASE 0.8711 vs ETS fijo 0.9949 (−12%): la auto-selección mejora. Matiz: ARIMA fijo MASE 0.9194 < AutoARIMA stepwise 0.9262 (aunque AutoARIMA mejor sMAPE: 14.01% vs 15.04%) | `OBSERVED` | Ídem F17 (SUMMARY_JSON del run) |
| F19 | Ledger tras capa 3: 4 ejercicios resueltos (0001:0.70→0, 0002:0.55→1, 0003:0.70→1, 0004:0.60→1); Brier 0.4900/0.2025/0.0900/0.1600; media real 0.2356 (n=4 — sin afirmaciones de calibración). pmdarima 2.1.1 añadido al stack (AutoARIMA) | `OBSERVED` | `oracle_status` + `pip install pmdarima` 2026-09-02 |

---

## 5. INFRAESTRUCTURA DE MEMORIA — ARCHIVOS DEL WORKSPACE

| Archivo | Función | Estado |
|---|---|---|
| `oracle_forecasts.jsonl` | Ledger auditable de pronósticos: ID, versión, probabilidad, supuestos, resolución, Brier Score | Operativo (0 registros) |
| `oracle_memory.md` | Memoria de contexto del ecosistema (este archivo) | Operativo v1.0 |
| `oracle_learnings.md` | Aprendizaje post-resolución y registro de calibración | Operativo v1.0 |
| `verify_stack.py` | Verificación ejecutable del stack: 7 métodos M4/M5-style reales (ajuste+pronóstico+error) | Operativo — `EXECUTED` 2026-09-02 (7/7 PASS) |
| `requirements.txt` | Dependencias de nivel superior del stack fpppy-aligned | Operativo |
| `requirements.lock.txt` | Versiones exactas congeladas (27 paquetes) | Operativo |
| `README_STACK.md` | Documentación del stack: ubicaciones, uso, mapa FPP→librería, replicabilidad, limitaciones | Operativo |
| `verify_stack_report.md` | Reporte auditable generado por `verify_stack.py` (MAE/RMSE/MASE/sMAPE por método) | Operativo — se regenera en cada ejecución |
| `fetch_m4_data.py` | Descarga del raw M4 oficial + extracción de muestra determinista (60 series mensuales) | Operativo — `EXECUTED` 2026-09-02 |
| `benchmark_m4.py` | Benchmark walk-forward M4 (2 folds expandentes, h=18, OWA oficial, ensemble) | Operativo — `EXECUTED` 2026-09-02 |
| `data/m4_monthly_sample.csv` | Muestra determinista 60 series M4 mensuales (longitudes 61–432) | Operativo |
| `m4_benchmark_report.md` / `m4_benchmark_results.csv` | Reporte y resultados largos del benchmark M4 | Operativo — regenerables |
| `benchmark_m4_auto.py` | Benchmark M4 con auto-selección por serie (AutoETS, AutoARIMA, ENSEMBLE-AUTO) | Operativo — `EXECUTED` 2026-09-02 |
| `m4_benchmark_auto_report.md` / `m4_benchmark_auto_results.csv` | Reporte y resultados del protocolo AUTO (959 filas) | Operativo — regenerables |
| `benchmark_m5h.py` | Pipeline M5-style jerárquico: Theta por nodo, BOTTOM-UP vs WLS-DIAG (proxy MinT) vs DIRECT, coherencia verificada | Operativo — `EXECUTED` 2026-09-02 |
| `m5_hierarchical_report.md` | Reporte del pipeline jerárquico (holdout final h=6) | Operativo — regenerable |

**Protocolo de actualización de memoria:**
1. Toda actualización relevante se registra en el changelog (sección 7).
2. Los hechos nuevos entran con etiqueta epistémica y fuente.
3. Los cambios de estado (p. ej. `PENDING_CONFIRMATION → VERIFIED`) exigen evidencia y quedan trazados.
4. Nunca se elimina información: se versiona (v1.0, v1.1, v2.0…).

---

## 5b. CORPUS ACADÉMICO — BIBLIOTECA DE FUNDAMENTACIÓN DE ORÁCULO (2026-09-02)

> Estado: estructura `VERIFIED` · verificación bibliográfica fina COMPLETADA 2026-09-02 (9 CORE-20 VERIFIED completas · 11 PARCIAL con huecos menores · 0 datos fabricados). Cierre de huecos DOI/ISBN pendiente: re-chequeo directo vía Crossref/doi.org desde entorno con red abierta.

- **Corpus:** 100 referencias (libros y papers) en 9 secciones temáticas, proporcionadas por el operador HITL y contrastadas por él con bibliografías actuales.
- **CORE-20:** núcleo obligatorio de conocimiento — IDs #1,#2,#3,#5,#6,#8,#9,#11,#16,#18,#20,#31,#32,#33,#41,#51,#53,#71,#81,#84.
- **Archivos del corpus:**
  - `bibliografia_master.md` — catálogo maestro navegable (100 refs + tabla de trazabilidad prompt→fundamentos).
  - `biblioteca_oracle.tsv` — versión machine-readable (columnas: id, sección, tipo, autores, título, año, core, rol).
  - `bibliografia_core20.md` — fichas verificadas del núcleo (9 VERIFIED · 11 PARCIAL · corrección Dawid JASA 1982 registrada).
- **Afirmación verificada:** edición Python de FPP ("fpppy") publicada en 2026 por OTexts (anuncio IIF 08-jun-2026, https://otexts.com/fpppy/). La fecha exacta "18-ago-2026" del operador: `NOT_VERIFIED`.
- **Rol predictivo del corpus:** tasas base, priors bayesianos y banco de evidencia citable para pronósticos (regla 26: EVIDENCE_QUALITY por fuente).
- **Razón empírica del enfoque (del operador):** M4 (61 métodos/100.000 series) y M5 (42.840 series jerárquicas) favorecen benchmarking, ensembles y evaluación fuera de muestra frente a lealtad dogmática a un modelo.

## 6. PRINCIPIOS PERMANENTES DE OPERACIÓN (resumen ejecutivo)

**Fuente:** prompt maestro ORÁCULO v1.0 — `VERIFIED`.

1. `PREDICCIÓN ≠ CERTEZA` — distinguir siempre hechos, datos, inferencias, supuestos, señales, ruido, escenarios, probabilidades e incertidumbre.
2. **Base rates first** — nunca ignorar tasas base por una narrativa convincente.
3. **Simplicidad adecuada** — `SIMPLEST ADEQUATE MODEL FIRST`; ensemble cuando existan varios modelos razonables.
4. **Escenarios** — mínimo: Base, Upside, Downside; Tail risk cuando el impacto lo justifique.
5. **Rangos antes que falsa precisión** — `55–65%` en vez de `61.3274%` salvo modelo cuantitativo justificado.
6. **Calibración sobre confianza** — `Probability ≠ Confidence`; un buen pronosticador busca estar calibrado, no parecer seguro.
7. **Actualización bayesiana versionada** — nunca sobrescribir silenciosamente; `FORECAST-001-v1 → v2 → v3`.
8. **Causalidad** — `CORRELATION ≠ CAUSATION`; vigilar confusores, sesgos de selección, survivorship, collider, etc.
9. **Red team obligatorio** — antes de emitir pronósticos importantes, intentar destruirlos.
10. **No hallucination** — prohibido inventar datos, resultados o simulaciones; `DATA_NOT_AVAILABLE`, `HEURISTIC_ESTIMATE`, `MODEL_NOT_EXECUTED` cuando corresponda.
11. **Criterio de parada** — `MARGINAL_INFORMATION_VALUE < ANALYSIS_COST` → detenerse.
12. **Alta consecuencia** — en dominios de alto riesgo elevar umbral de evidencia y recomendar revisión profesional.
13. **Output contract** — todo pronóstico importante cierra con `ORACLE_STATUS`, `PREDICTION`, `PROBABILITY`, `CONFIDENCE`, `DATA_QUALITY`, `FORECAST_FRAGILITY`, `MAIN_ASSUMPTION`, `MAIN_RISK`, `UPDATE_TRIGGER`.

---

## 7. CHANGELOG

| Versión | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-09-02 | Creación del archivo de memoria persistente | ORÁCULO |
| 1.1 | 2026-09-02 | Alta del corpus académico (100 refs, CORE-20, archivos de biblioteca) | ORÁCULO |
| 1.2 | 2026-09-02 | Verificación bibliográfica completada; alta de fichas `bibliografia_core20.md`; corrección Dawid (JASA 1982) | ORÁCULO |
| 1.3 | 2026-09-02 | Esqueleto ejecutable (capa 1): venv Python 3.14.7 + stack statsmodels/scikit-learn/sktime instalado y verificado 7/7 con métodos M4/M5-style reales; alta de `verify_stack.py`, `requirements.txt`, `requirements.lock.txt`, `README_STACK.md` | ORÁCULO |
| 1.4 | 2026-09-02 | Capa 2: datos M4 reales + benchmark walk-forward (Theta/ENSEMBLE/ARIMA/ETS vs SNaive, OWA); primeros registros resueltos del ledger como EJERCICIO pre-registrado (0001: 0.70→0, 0002: 0.55→1); APRENDIZAJE-001; alta de `fetch_m4_data.py`, `benchmark_m4.py`, `data/`, reports | ORÁCULO |
| 1.5 | 2026-09-02 | Capa 3: benchmark protocolo AUTO (AutoETS/AutoARIMA/ENSEMBLE-AUTO; 0003: 0.70→1 Brier 0.09, 0004: 0.60→1 Brier 0.16) + pipeline M5 jerárquico con reconciliación WLS-DIAG verificado (coherencia 8.7e-11); APRENDIZAJE-002; pmdarima al stack; Brier medio real 0.2356 (n=4) | ORÁCULO |
