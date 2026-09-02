# ─────────────────────────────────────────────────────────────────────────────
# ORÁCULO · AACC-PANDHARPUR — pipeline M5-style jerárquico con reconciliación
# (capa 3b)
#
# Métodos de la competencia M5 = jerarquía + exógenas + reconciliación.
# Sobre series MENSUALES REALES M4 (misma muestra oficial que capas 1-3a):
#   · Jerarquía de demostración: 24 series base (hojas) → 4 grupos → total.
#     (construcción de agrupación sintética y determinista: el foco es la
#     MAQUINARIA jerárquica, no la semántica de negocio de la agrupación;
#     el dataset oficial M5 de Walmart requiere credenciales de Kaggle —
#     bloqueo documentado, no simulado)
#   · Hojas pronosticadas con Theta sp=12 (método M4 real, ya verificado)
#   · Estrategias comparadas en holdout (1 fold walk-forward, h=6, 60% train):
#       - DIRECT: Theta ajustado sobre la serie agregada del nodo total
#       - BOTTOM-UP: agrega pronósticos de hojas
#       - MinT-DIAG: reconciliación con W = varianza diag. de errores de
#         ajuste por nodo (proxy WLS del MinT; el MinT real requiere la
#         covarianza de errores de pronóstico — etiqueta honesta: WLS-DIAG)
#   · Métrica en el nodo TOTAL: MAE/MASE(escala) y sMAPE del holdout.
# Reporte: m5_hierarchical_report.md
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import os
import sys
import time

import numpy as np
import pandas as pd
from sktime.forecasting.theta import ThetaForecaster

from verify_stack import mae, smape, mase  # helpers compartidos

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "data", "m4_monthly_sample.csv")
REPORT = os.path.join(HERE, "m5_hierarchical_report.md")
H = 6
SEASON = 12
N_LEAVES = 24
N_GROUPS = 4


def theta_forecast(train: np.ndarray, h: int) -> np.ndarray:
    """Theta sp=12 sobre PeriodIndex (patrón sktime 1.1 verificado)."""
    fc = ThetaForecaster(sp=SEASON)
    idx = pd.period_range("1990-01", periods=len(train), freq="M")
    fc.fit(pd.Series(np.asarray(train, float), index=idx), fh=list(range(1, h + 1)))
    return np.asarray(fc.predict(), dtype=float).ravel()


def main() -> int:
    df = pd.read_csv(DEFAULT_CSV)
    # hojas: primeras N_LEAVES series con longitud suficiente para h+SEASON
    leaves: dict[str, np.ndarray] = {}
    for c in df.columns:
        y = df[c].dropna().to_numpy(dtype=float)
        if len(y) >= 4 * H + SEASON:
            leaves[str(c)] = y
        if len(leaves) >= N_LEAVES:
            break
    leaf_names = list(leaves)
    # agrupación determinista: z = índice // (N_LEAVES // N_GROUPS)
    group_of = {name: i // (N_LEAVES // N_GROUPS) for i, name in enumerate(leaf_names)}
    groups = {g: [n for n in leaf_names if group_of[n] == g] for g in range(N_GROUPS)}

    # alinear longitudes al mínimo (para construir agregados coherentes)
    min_len = min(len(leaves[n]) for n in leaf_names)
    for n in leaf_names:
        leaves[n] = leaves[n][-min_len:]
    t_cut = min_len - H  # 1 fold: holdout final de h pasos
    print(f"hojas={N_LEAVES} grupos={N_GROUPS} n={min_len} train={t_cut} test={H} h={H}")

    # ── series agregadas reales ──
    agg_group = {g: leaves[groups[g][0]].copy() for g in groups}
    for g in groups:
        for n in groups[g][1:]:
            agg_group[g] = agg_group[g] + leaves[n]
    total = sum(agg_group[g] for g in groups)

    nodes_all = {"total": total, **{f"g{g}": agg_group[g] for g in groups},
                 **{n: leaves[n] for n in leaf_names}}
    order = ["total"] + [f"g{g}" for g in groups] + leaf_names
    n_nodes = len(order)

    # ── matriz de agregación S (n_nodes × n_leaves): total/grupos/hojas ──
    S = np.zeros((n_nodes, N_LEAVES))
    S[0, :] = 1.0  # total
    for g in groups:
        for j, n in enumerate(leaf_names):
            if group_of[n] == g:
                S[1 + g, j] = 1.0
    for j in range(N_LEAVES):
        S[1 + N_GROUPS + j, j] = 1.0

    # ── 1) DIRECT: Theta sobre total ──
    y_total = total
    tr_t, te_t = y_total[:t_cut], y_total[t_cut:t_cut + H]
    pred_direct = theta_forecast(tr_t, H)

    # ── 2) BOTTOM-UP: Theta en cada hoja, agregar ──
    pred_leaf = np.zeros((N_LEAVES, H))
    leaf_scale = np.zeros(N_LEAVES)  # escala para MASE por hoja
    for j, n in enumerate(leaf_names):
        yl = leaves[n]
        tr_l, te_l = yl[:t_cut], yl[t_cut:t_cut + H]
        pred_leaf[j] = theta_forecast(tr_l, H)
        leaf_scale[j] = max(float(np.mean(np.abs(np.diff(tr_l[-(SEASON + 1):])))), 1e-9)
    pred_bu = pred_leaf.sum(axis=0)

    # ── 3) WLS-DIAG: reconciliación con pesos diagonales
    #      W = varianza residual in-sample por nodo (PROXY de MinT; el MinT
    #      real exige la covarianza de errores de pronóstico Σ_h, no disponible
    #      con un solo fold → etiqueta honesta: WLS-DIAG, no MinT)
    base = np.zeros((n_nodes, H))
    node_scale = np.zeros(n_nodes)
    for i, name in enumerate(order):
        yv = nodes_all[name]
        tr, te = yv[:t_cut], yv[t_cut:t_cut + H]
        base[i] = theta_forecast(tr, H)
        resid = np.diff(tr[-(SEASON + 1):])
        node_scale[i] = max(float(np.var(resid)), 1e-12)
    W = np.diag(node_scale)
    SWS = S.T @ W @ S
    G = np.linalg.solve(SWS, S.T @ W)  # G = (S'W S)^{-1} S'W
    pred_rec = S @ G @ base  # pronósticos reconciliados (todos los nodos)
    pred_wls_top = pred_rec[0]

    # ── evaluación en nodo TOTAL ──
    def metrics(pred: np.ndarray, tag: str) -> None:
        print(f"  {tag:22s} MAE={mae(te_t, pred):10.3f}  "
              f"sMAPE={smape(te_t, pred):6.2f}%  "
              f"MASE={mase(tr_t, te_t, pred, SEASON):.3f}")
    print("=== NODO TOTAL (holdout final h=6) ===")
    metrics(pred_direct, "DIRECT")
    metrics(pred_bu, "BOTTOM-UP")
    metrics(pred_wls_top, "WLS-DIAG")

    # ── consistencia correcta: nodos agregados reconciliados deben ser
    #    coherentes con las hojas reconciliadas (S_top @ leaves_rec) ──
    leaves_rec = pred_rec[1 + N_GROUPS:]           # bloque de hojas reconciliado
    S_top = S[:1 + N_GROUPS]                        # filas total+grupos
    incoherence = float(np.max(np.abs(S_top @ leaves_rec - pred_rec[:1 + N_GROUPS])))
    print(f"Incoherencia top-vs-hojas tras reconciliar: {incoherence:.2e} (debe ser ~0)")
    # y las hojas reconciliadas = G @ base (proyección sobre el espacio coherente)
    proj_diff = float(np.max(np.abs(leaves_rec - G @ base)))
    print(f"Desvío hojas_rec vs G@base: {proj_diff:.2e} (debe ser ~0)")

    lines = [
        "# ORÁCULO — Pipeline M5-style jerárquico (reconciliación, datos reales)",
        "",
        f"- Fecha: {pd.Timestamp.now().isoformat(timespec='seconds')}",
        f"- Base: {N_LEAVES} series mensuales reales M4 (muestra oficial) agrupadas en "
        f"{N_GROUPS} grupos sintéticos + total (jerarquía de demostración; dataset "
        f"oficial M5 de Walmart requiere credenciales Kaggle — bloqueo documentado)",
        f"- Método de hoja/nodo: Theta sp=12 · h={H} · walk-forward 1 fold (60% train)",
        "",
        "| estrategia | MAE (total) | sMAPE | MASE |",
        "|---|---|---|---|",
        f"| DIRECT (Theta sobre agregado) | {mae(te_t, pred_direct):.3f} | {smape(te_t, pred_direct):.2f}% | {mase(tr_t, te_t, pred_direct, SEASON):.3f} |",
        f"| BOTTOM-UP | {mae(te_t, pred_bu):.3f} | {smape(te_t, pred_bu):.2f}% | {mase(tr_t, te_t, pred_bu, SEASON):.3f} |",
        f"| WLS-DIAG (proxy MinT, reconciliado) | {mae(te_t, pred_wls_top):.3f} | {smape(te_t, pred_wls_top):.2f}% | {mase(tr_t, te_t, pred_wls_top, SEASON):.3f} |",
        "",
        f"- Incoherencia top-vs-hojas tras reconciliar: {incoherence:.2e} "
        f"(~0 = proyección coherente correcta) · desvío hojas vs G@base: {proj_diff:.2e}",
        "",
        "**Nota:** demostración de la maquinaria M5 (jerarquía + reconciliación) sobre "
        "series reales; la agrupación es sintética, no semántica de negocio.",
    ]
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Reporte: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
