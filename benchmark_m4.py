# ─────────────────────────────────────────────────────────────────────────────
# ORÁCULO · AACC-PANDHARPUR — benchmark walk-forward M4 (datos reales)
#
# Walk-forward sobre muestra oficial M4 mensual (fetch_m4_data.py), h=18
# (horizonte oficial M4 monthly), 2 folds expandentes por serie:
#   fold 1: train = [0, n-36), test = [n-36, n-18)
#   fold 2: train = [0, n-18), test = [n-18, n)
# Métodos: SeasonalNaive (baseline OWA), Theta (sktime), ETS y ARIMA
# (statsmodels), y ENSEMBLE = media simple de Theta+ETS+ARIMA (Bates–Granger,
# pesos iguales — sin tuning sobre estos datos).
# Métricas: MASE y sMAPE por fold (escaladas al SNaive in-sample de cada fold),
# OWA oficial M4 = (sMAPE_rel + MASE_rel)/2 frente a SeasonalNaive.
#
# Nota epistémica: benchmark de infraestructura sobre datos ya observados
# (evaluación de métodos, no pronóstico de eventos futuros). No produce
# entradas de calibración del ledger por sí mismo.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from sktime.forecasting.theta import ThetaForecaster

from verify_stack import mae, smape, mase  # helpers compartidos (workspace)

H = 18          # horizonte oficial M4 mensual
FOLD_CUTS = [2 * H, H]  # n - 2H y n - H
SEASON = 12
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "data", "m4_monthly_sample.csv")
REPORT = os.path.join(HERE, "m4_benchmark_report.md")
RESULTS_CSV = os.path.join(HERE, "m4_benchmark_results.csv")

METHODS = ("SeasonalNaive", "Theta", "ETS", "ARIMA", "ENSEMBLE")


def seasonal_naive_pred(train: np.ndarray, h: int) -> np.ndarray:
    """Predicción naive estacional (periodo 12) para h pasos."""
    k = int(np.ceil(h / SEASON))
    return np.tile(train[-SEASON:], k)[:h]


def theta_pred(train: np.ndarray, h: int) -> np.ndarray:
    fc = ThetaForecaster(sp=SEASON)
    idx = pd.period_range("1990-01", periods=len(train), freq="M")
    s = pd.Series(np.asarray(train, float), index=idx)
    fc.fit(s, fh=list(range(1, h + 1)))
    return np.asarray(fc.predict(), dtype=float).ravel()


def ets_pred(train: np.ndarray, h: int) -> np.ndarray:
    idx = pd.date_range("1990-01-01", periods=len(train), freq="MS")
    s = pd.Series(np.asarray(train, float), index=idx)
    model = ETSModel(s, error="add", trend="add", seasonal="add",
                     seasonal_periods=SEASON, initialization_method="estimated")
    res = model.fit(disp=False)
    return np.asarray(res.forecast(h)).ravel()


def arima_pred(train: np.ndarray, h: int) -> np.ndarray:
    idx = pd.date_range("1990-01-01", periods=len(train), freq="MS")
    s = pd.Series(np.asarray(train, float), index=idx)
    model = ARIMA(s, order=(1, 1, 1), seasonal_order=(0, 1, 1, SEASON))
    res = model.fit()
    return np.asarray(res.forecast(h)).ravel()


PREDICTORS = {"Theta": theta_pred, "ETS": ets_pred, "ARIMA": arima_pred}


def run() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=DEFAULT_CSV)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    series_cols = [c for c in df.columns]
    print(f"CSV: {args.csv} · {len(series_cols)} series candidatas")

    rows: list[dict] = []
    errors: dict[str, int] = {m: 0 for m in METHODS}
    n_used = 0
    t_start = time.time()

    for col in series_cols:
        y = df[col].dropna().to_numpy(dtype=float)
        n = len(y)
        if n < 2 * H + SEASON + 1:  # necesitamos train mínimo con estacionalidad
            continue
        n_used += 1
        for cut in FOLD_CUTS:
            tr_end = n - cut
            train, test = y[:tr_end], y[tr_end:tr_end + H]
            if len(test) < H:
                continue
            preds: dict[str, np.ndarray | None] = {"SeasonalNaive": seasonal_naive_pred(train, H)}
            for name, fn in PREDICTORS.items():
                try:
                    preds[name] = fn(train, H)
                except Exception as exc:  # noqa: BLE001 — robustez por serie
                    errors[name] += 1
                    preds[name] = None
                    print(f"  [warn] {col} fold n-{cut} {name}: {exc}", flush=True)
            avail = [preds[m] for m in ("Theta", "ETS", "ARIMA") if preds[m] is not None]
            if avail:
                preds["ENSEMBLE"] = np.mean(avail, axis=0)
            else:
                preds["ENSEMBLE"] = None
                errors["ENSEMBLE"] += 1

            for m in METHODS:
                p = preds[m]
                if p is None:
                    continue
                rows.append({
                    "series": col, "fold_train_end": int(tr_end),
                    "method": m, "mase": mase(train, test, p, SEASON),
                    "smape": smape(test, p), "mae": mae(test, p),
                })
        if n_used % 10 == 0:
            print(f"  ... {n_used} series procesadas "
                  f"({time.time() - t_start:.0f}s)", flush=True)

    if not rows:
        print("ERROR: sin filas evaluables", file=sys.stderr)
        return 1
    res = pd.DataFrame(rows)
    res.to_csv(RESULTS_CSV, index=False)
    print(f"Resultados largos: {RESULTS_CSV} ({len(res)} filas, "
          f"{time.time() - t_start:.0f}s)")

    # ── agregación: media por serie (2 folds) y luego media entre series ──
    by_series = (res.groupby(["series", "method"])[["mase", "smape"]]
                 .mean().reset_index())
    agg = (by_series.groupby("method")[["mase", "smape"]]
           .mean().sort_values("mase"))
    snaive = agg.loc["SeasonalNaive"]
    agg["owa"] = 0.5 * (agg["smape"] / snaive["smape"]
                        + agg["mase"] / snaive["mase"])

    # frecuencia de victoria vs SeasonalNaive (MASE medio por serie)
    pivot = by_series.pivot(index="series", columns="method", values="mase")
    win_rows = []
    for m in METHODS:
        if m == "SeasonalNaive" or m not in pivot:
            continue
        win_rows.append({"method": m, "wins_vs_snaive": float((pivot[m] < pivot["SeasonalNaive"]).mean())})
    wins = pd.DataFrame(win_rows).set_index("method") if win_rows else pd.DataFrame()

    print("\n=== AGRECADO (media de MASE/sMAPE medios por serie) ===")
    print(agg.round(4).to_string())
    if len(wins):
        print("\n=== FRECUENCIA de victoria vs SeasonalNaive (MASE por serie) ===")
        print(wins.round(3).to_string())

    # ── reporte ──
    lines = [
        "# ORÁCULO — Benchmark walk-forward M4 (datos reales, muestra oficial)",
        "",
        f"- Fecha: {pd.Timestamp.now().isoformat(timespec='seconds')}",
        f"- Fuente: Mcompetitions/M4-methods (Monthly-train.csv), muestra determinista",
        f"- Series evaluadas: {n_used} · folds por serie: {len(FOLD_CUTS)} · h={H}",
        f"- Filas de evaluación: {len(res)} · errores de ajuste: {errors}",
        "",
        "| método | MASE medio | sMAPE medio | OWA (vs SNaive) |",
        "|---|---|---|---|",
    ]
    order = agg.sort_values("owa").index
    for m in order:
        r = agg.loc[m]
        lines.append(f"| {m} | {r['mase']:.4f} | {r['smape']:.2f}% | {r['owa']:.4f} |")
    lines += ["", "**OJO:** benchmark de infraestructura sobre datos ya observados "
                  "(evaluación de métodos M4-style); no es un pronóstico de eventos "
                  "futuros ni entrada de calibración del ledger."]
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nReporte: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
