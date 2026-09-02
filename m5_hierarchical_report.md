# ORÁCULO — Pipeline M5-style jerárquico (reconciliación, datos reales)

- Fecha: 2026-09-02T08:17:00
- Base: 24 series mensuales reales M4 (muestra oficial) agrupadas en 4 grupos sintéticos + total (jerarquía de demostración; dataset oficial M5 de Walmart requiere credenciales Kaggle — bloqueo documentado)
- Método de hoja/nodo: Theta sp=12 · h=6 · walk-forward 1 fold (60% train)

| estrategia | MAE (total) | sMAPE | MASE |
|---|---|---|---|
| DIRECT (Theta sobre agregado) | 17556.489 | 12.61% | 2.570 |
| BOTTOM-UP | 21403.763 | 15.09% | 3.133 |
| WLS-DIAG (proxy MinT, reconciliado) | 17559.794 | 12.61% | 2.570 |

- Incoherencia top-vs-hojas tras reconciliar: 8.73e-11 (~0 = proyección coherente correcta) · desvío hojas vs G@base: 0.00e+00

**Nota:** demostración de la maquinaria M5 (jerarquía + reconciliación) sobre series reales; la agrupación es sintética, no semántica de negocio.
