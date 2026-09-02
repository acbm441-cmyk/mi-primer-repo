# 📚 ORÁCULO — REGISTRO DE APRENDIZAJE Y CALIBRACIÓN

> **Tipo de archivo:** Aprendizaje post-resolución y registro de calibración del agente ORÁCULO.
> **Ruta:** `C:\Users\ACBM\OneDrive\Documentos\DEEPSEEK\ORACLE\oracle_learnings.md`
> **Versión:** 1.0 · **Creado:** 2026-09-02 · **Modelo:** deepseek-v4-flash
> **Regla:** este archivo solo documenta aprendizajes REALES derivados de pronósticos RESUELTOS en el ledger (`oracle_forecasts.jsonl`). No se registran aprendizajes ficticios ni se extrapolan lecciones de pronósticos no resueltos.

---

## 1. ESTADO DE CALIBRACIÓN ACTUAL — `VERIFIED` (2026-09-02)

| Métrica | Valor | Nota |
|---|---|---|
| Pronósticos registrados | 4 | Todos = EJERCICIO metodológico pre-registrado (no eventos temporales reales) |
| Pronósticos resueltos | 4 | 0001 (0.70→0) · 0002 (0.55→1) · 0003 (0.70→1) · 0004 (0.60→1) |
| Brier medio | 0.2356 | Real, calculado por el ledger sobre n=4 |
| Tasa empírica por decil | — | No interpretable (n=4; bucket 0.7–0.8 con 1/2 sugiere vigilancia) |

**Implicación:** ORÁCULO NO extrae conclusiones de calibración propias con n<30. Los registros son ejercicios etiquetados; la calibración real se medirá sobre pronósticos de eventos del mundo con resolución temporal genuina.

---

## 2. PROTOCOLO DE APRENDIZAJE POST-RESOLUCIÓN

Cuando un pronóstico del ledger se resuelva (`oracle_resolve` con outcome 1/0), ejecutar este ciclo:

```
FORECAST → OUTCOME → ERROR → CALIBRATION → MODEL UPDATE → IMPROVED FORECAST
```

Y documentar en la sección 3 una entrada con:

- `FORECAST_ID` y versión(es) implicadas
- Pregunta y horizonte
- Probabilidad emitida vs. desenlace (1/0)
- Brier Score real (lo calcula el ledger)
- `WHAT WAS RIGHT` — qué acierto
- `WHAT WAS WRONG` — qué falló
- `WHICH ASSUMPTION FAILED` — qué supuesto del assumption ledger falló
- `WHICH SIGNAL MATTERED` — qué señal era real
- `WHICH SIGNAL WAS NOISE` — qué señal era ruido
- `CALIBRATION LESSON` — lección generalizable (sin overfitting a un caso)

**Anti-overfitting (regla 48):** una sola resolución NO justifica cambiar las reglas generales. Solo patrones repetidos (≥3–5 casos) deben promover una actualización de metodología.

---

## 3. ENTRADAS DE APRENDIZAJE

### APRENDIZAJE-001 · ORACLE-2026-0001 (+0002) · 2026-09-02

> **Naturaleza del evento:** EJERCICIO metodológico pre-registrado sobre benchmark M4 (datos reales, 60 series mensuales oficiales, walk-forward 2×18). NO es un evento temporal del mundo real: etiquetado explícitamente para no contaminar la calibración de pronósticos reales.

- **Pregunta 0001:** ¿ENSEMBLE media-simple (Theta+ETS+ARIMA) supera al mejor individual en OWA? | **P=0.70**
- **Pregunta 0002:** ¿ARIMA(1,1,1)(0,1,1)₁₂ tiene MASE medio < ETS add/add/add? | **P=0.55**
- **Desenlaces:** 0001 → 0 (Theta OWA 0.7373 < ENSEMBLE 0.8054) | 0002 → 1 (ARIMA 0.9194 < ETS 0.9949)
- **Brier Score real:** 0001 = 0.4900 | 0002 = 0.2025
- **WHAT WAS RIGHT:** el prior casi-coin-flip (0.55) de 0002 estaba bien calibrado: ARIMA vs ETS con especificaciones fijas es un empate técnico que en esta muestra se decantó por ARIMA. El prior de M4 oficial (los métodos superan al naive) se confirmó: todos MASE<1, victoria vs SNaive 67–77% de series.
- **WHAT WAS WRONG:** el prior de 0001 (0.70 a favor del ensemble) fue **sobreconfiado**: el ensemble perdió contra Theta. El ancla vino de la conclusión agregada de M4 ("las combinaciones ganan"), que no se transfiere a este pipeline.
- **WHICH ASSUMPTION FAILED:** "combinar siempre mejora" — falso cuando los componentes no tienen calidad comparable: ETS/ARIMA con especificación fija (sin auto-selección por serie) son componentes débiles que diluyen al ensemble; Theta (con deseasonalización adaptativa interna) dominó en solitario.
- **WHICH SIGNAL MATTERED:** Theta es robusto en mensuales M4 reales incluso contra modelos de espacio de estados fijos; el ranking OWA discrimina bien entre pipelines (0.74 → 1.0).
- **WHICH SIGNAL WAS NOISE:** la narrativa agregada de M4 sobre combinaciones; los resultados por frecuencia y por especificación concreta varían sustancialmente.
- **CALIBRATION LESSON (provisional):** no extrapolar conclusiones de M4 global (donde los métodos se auto-seleccionan por serie) a pipelines de especificación fija; evaluar ensembles solo con componentes de calidad comparable o pesos basados en validación. Anti-overfitting (regla 48): n=1 ejercicio — NO se cambia metodología general todavía.

### APRENDIZAJE-002 · ORACLE-2026-0003 (+0004) · 2026-09-02

> **Naturaleza:** EJERCICIO metodológico pre-registrado (benchmark M4 auto-selección, 60 series reales). No es evento temporal real.

- **Pregunta 0003:** ¿AutoETS(auto) MASE medio < ETS add/add/add fijo? | **P=0.70**
- **Pregunta 0004:** ¿ENSEMBLE-AUTO (Theta+AutoETS+AutoARIMA) OWA < Theta? | **P=0.60**
- **Desenlaces:** 0003 → 1 (0.8711 < 0.9949) | 0004 → 1 (OWA 0.7221 < 0.7373)
- **Brier Score real:** 0003 = 0.0900 | 0004 = 0.1600
- **WHAT WAS RIGHT:** ambas hipótesis. La auto-selección de especificación ETS mejora el MASE ~12%. Y el corolario de APRENDIZAJE-001 se confirmó: con componentes de calidad comparable (AutoETS/AutoARIMA ≈ Theta), el ENSEMBLE-AUTO (0.7221) supera al mejor individual (Theta, 0.7373) — el mismo ensemble-fijo con componentes débiles había perdido en capa 2 (0.8054).
- **WHAT WAS WRONG:** matiz revelador: AutoARIMA stepwise (MASE 0.9262) NO superó al ARIMA fijo (0.9194) en MASE, aunque sí en sMAPE (14.01% vs 15.04%). La flexibilidad automática no garantiza ganancia.
- **WHICH ASSUMPTION FAILED:** ninguna de las dos centrales; la presunción implícita "más auto-selección siempre mejora" quedó refutada para AutoARIMA en MASE.
- **WHICH SIGNAL MATTERED:** la calidad comparable de los componentes (métricas auto ≈ Theta) es el predictor de cuándo el ensemble añade valor — señal accionable para diseñar combinaciones.
- **WHICH SIGNAL WAS NOISE:** la narrativa "auto siempre gana"; en esta muestra el ARIMA fijo aguantó mejor en MASE.
- **CALIBRATION LESSON:** 4 resoluciones de ejercicio acumuladas (Brier: 0.49, 0.2025, 0.09, 0.16; media real 0.2356). Señal temprana de sobreconfianza en el bucket 0.7–0.8 (2 eventos, 1 acierto). n<30: se mantiene vigilancia sin cambios metodológicos.

### Plantilla de entrada

```markdown
### APRENDIZAJE-### · [FORECAST_ID] · [YYYY-MM-DD]

- **Pregunta:** …
- **Horizonte:** …
- **Probabilidad emitida:** … | **Desenlace:** 1/0 | **Brier Score:** …
- **WHAT WAS RIGHT:** …
- **WHAT WAS WRONG:** …
- **WHICH ASSUMPTION FAILED:** …
- **WHICH SIGNAL MATTERED:** …
- **WHICH SIGNAL WAS NOISE:** …
- **CALIBRATION LESSON:** …
```

---

## 4. REVISIONES METODOLÓGICAS (solo tras patrones repetidos)

| Fecha | Lección | Evidencia (nº de resoluciones) | Cambio metodológico |
|---|---|---|---|
| — | — | — | — |

---

## 5. CHANGELOG

| Versión | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-09-02 | Creación del registro de aprendizaje y calibración | ORÁCULO |
| 1.1 | 2026-09-02 | Primera entrada APRENDIZAJE-001 (ejercicio pre-registrado M4, ORACLE-2026-0001/0002 resueltos con Brier real) | ORÁCULO |
| 1.2 | 2026-09-02 | APRENDIZAJE-002 (capa 3: ORACLE-2026-0003/0004 resueltos, auto-selección y ensemble-auto confirmados; Brier medio real 0.2356 con n=4) | ORÁCULO |
