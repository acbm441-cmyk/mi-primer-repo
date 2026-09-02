# ─────────────────────────────────────────────────────────────────────────────
# ORÁCULO · AACC-PANDHARPUR — benchmark M4 protocolo AUTO (capa 3)
#
# Misma muestra real M4 mensual, mismos folds (2×18, walk-forward expandente),
# que benchmark_m4.py — pero ahora con auto-selección por serie, acercándose
# al protocolo oficial M4 (donde los métodos se eligen por serie):
#   SeasonalNaive · Theta · ETS fijo · ARIMA fijo · AutoETS(auto=True) ·
#   AutoARIMA (pmdarima, si está disponible) · ENSEMBLE-AUTO ·
#   ENSEMBLE-FIXED (control, mismo que capa 2)
#
# ENSEMBLE-AUTO = media simple de los auto/optimizados disponibles
# (Theta + AutoETS + AutoARIMA si corre; si AutoARIMA no está, Theta + AutoETS).
# Composición fijada y reportada — sin tuning sobre estos datos.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from sktime.forecasting.theta import ThetaForecaster

from verify_stack import mae, smape, mase  # helpers compartidos

H = 18
FOLD_CUTS = [2 * H, H]
SEASON = 12
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "data", "m4_monthly_sample.csv")
REPORT = os.path.join(HERE, "m4_benchmark_auto_report.md")
RESULTS_CSV = os.path.join(HERE, "m4_benchmark_auto_results.csv")


def seasonal_naive_pred(train: np.ndarray, h: int) -> np.ndarray:
    k = int(np.ceil(h / SEASON))
    return np.tile(train[-SEASON:], k)[:h]


def sktime_period_series(train: np.ndarray):
    idx = pd.period_range("1990-01", periods=len(train), freq="M")
    return pd.Series(np.asarray(train, float), index=idx)


def theta_pred(train: np.ndarray, h: int) -> np.ndarray:
    fc = ThetaForecaster(sp=SEASON)
    fc.fit(sktime_period_series(train), fh=list(range(1, h + 1)))
    return np.asarray(fc.predict(), dtype=float).ravel()


def ets_fixed_pred(train: np.ndarray, h: int) -> np.ndarray:
    model = ETSModel(pd.Series(train, index=pd.date_range("1990-01-01",
                     periods=len(train), freq="MS")), error="add", trend="add",
                     seasonal="add", seasonal_periods=SEASON,
                     initialization_method="estimated")
    return np.asarray(model.fit(disp=False).forecast(h)).ravel()


def arima_fixed_pred(train: np.ndarray, h: int) -> np.ndarray:
    model = ARIMA(pd.Series(train, index=pd.date_range("1990-01-01",
                  periods=len(train), freq="MS")), order=(1, 1, 1),
                  seasonal_order=(0, 1, 1, SEASON))
    return np.asarray(model.fit().forecast(h)).ravel()


def autoets_pred(train: np.ndarray, h: int) -> np.ndarray:
    from sktime.forecasting.ets import AutoETS
    fc = AutoETS(auto=True, sp=SEASON, maxiter=1000)
    fc.fit(sktime_period_series(train), fh=list(range(1, h + 1)))
    return np.asarray(fc.predict(), dtype=float).ravel()


_AUTOARIMA_AVAILABLE = False


def try_autoarima():
    global _AUTOARIMA_AVAILABLE
    try:
        from sktime.forecasting.arima import AutoARIMA
        _AUTOARIMA_AVAILABLE = True
        print("AutoARIMA (pmdarima): DISPONIBLE", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"AutoARIMA (pmdarima): NO disponible ({exc})", flush=True)


def autoarima_pred(train: np.ndarray, h: int) -> np.ndarray:
    from sktime.forecasting.arima import AutoARIMA
    fc = AutoARIMA(sp=SEASON, information_criterion="aic",
                   seasonal=True, stepwise=True, n_jobs=1)
    fc.fit(sktime_period_series(train), fh=list(range(1, h + 1)))
    return np.asarray(fc.predict(), dtype=float).ravel()


def run() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=DEFAULT_CSV)
    args = ap.parse_args()
    try_autoarima()

    df = pd.read_csv(args.csv)
    series_cols = [c for c in df.columns]
    print(f"CSV: {args.csv} · {len(series_cols)} series · h={H} · folds={len(FOLD_CUTS)}")

    METHODS = ["SeasonalNaive", "Theta", "ETS-fixed", "ARIMA-fixed"]
    if _AUTOARIMA_AVAILABLE:
        METHODS.append("AutoARIMA")
    METHODS += ["AutoETS", "ENSEMBLE-AUTO", "ENSEMBLE-FIXED"]
    errors = {m: 0 for m in METHODS}

    rows: list[dict] = []
    n_used = 0
    t0 = time.time()
    for col in series_cols:
        y = df[col].dropna().to_numpy(dtype=float)
        n = len(y)
        if n < 2 * H + SEASON + 1:
            continue
        n_used += 1
        for cut in FOLD_CUTS:
            tr_end = n - cut
            train, test = y[:tr_end], y[tr_end:tr_end + H]
            if len(test) < H:
                continue
            preds: dict[str, np.ndarray | None] = {}
            specs = {"SeasonalNaive": seasonal_naive_pred,
                     "Theta": theta_pred, "ETS-fixed": ets_fixed_pred,
                     "ARIMA-fixed": arima_fixed_pred,
                     "AutoETS": autoets_pred}
            if _AUTOARIMA_AVAILABLE:
                specs["AutoARIMA"] = autoarima_pred
            for name, fn in specs.items():
                try:
                    preds[name] = fn(train, H)
                except Exception as exc:  # noqa: BLE001
                    errors[name] += 1
                    preds[name] = None
                    print(f"  [warn] {col} fold n-{cut} {name}: {exc}", flush=True)
            if _AUTOARIMA_AVAILABLE:
                ens_auto = [preds[m] for m in ("Theta", "AutoETS", "AutoARIMA")]
            else:
                ens_auto = [preds[m] for m in ("Theta", "AutoETS")]
            ens_auto = [p for p in ens_auto if p is not None]
            ens_fixed = [preds[m] for m in ("Theta", "ETS-fixed", "ARIMA-fixed")]
            ens_fixed = [p for p in ens_fixed if p is not None]
            if ens_auto:
                preds["ENSEMBLE-AUTO"] = np.mean(ens_auto, axis=0)
            else:
                preds["ENSEMBLE-AUTO"] = None
                errors["ENSEMBLE-AUTO"] += 1
            if ens_fixed:
                preds["ENSEMBLE-FIXED"] = np.mean(ens_fixed, axis=0)
            else:
                preds["ENSEMBLE-FIXED"] = None
                errors["ENSEMBLE-FIXED"] += 1
            for m in METHODS:
                p = preds[m]
                if p is None:
                    continue
                rows.append({"series": col, "fold_train_end": int(tr_end),
                             "method": m, "mase": mase(train, test, p, SEASON),
                             "smape": smape(test, p), "mae": mae(test, p)})
        if n_used % 10 == 0:
            print(f"  ... {n_used} series ({time.time() - t0:.0f}s)", flush=True)

    if not rows:
        print("ERROR: sin filas evaluables", file=sys.stderr)
        return 1
    res = pd.DataFrame(rows)
    res.to_csv(RESULTS_CSV, index=False)
    print(f"Resultados: {RESULTS_CSV} ({len(res)} filas, {time.time() - t0:.0f}s)")

    by_series = (res.groupby(["series", "method"])[["mase", "smape"]]
                 .mean().reset_index())
    agg = by_series.groupby("method")[["mase", "smape"]].mean()
    snaive = agg.loc["SeasonalNaive"]
    agg["owa"] = 0.5 * (agg["smape"] / snaive["smape"] + agg["mase"] / snaive["mase"])
    agg = agg.sort_values("owa")

    print("\n=== AGRECADO (OWA vs SeasonalNaive, ordenado) ===")
    print(agg.round(4).to_string())

    # ── métricas clave para resolución del ledger (impresas en JSON) ──
    def mm(name):
        return float(agg.loc[name, "mase"]) if name in agg.index else float("nan")
    summary = {
        "n_series": n_used, "errors": errors,
        "mase_autoets": mm("AutoETS"), "mase_ets_fixed": mm("ETS-fixed"),
        "mase_arima_fixed": mm("ARIMA-fixed"),
        "owa_ensemble_auto": float(agg.loc["ENSEMBLE-AUTO", "owa"]),
        "owa_theta": float(agg.loc["Theta", "owa"]),
        "owa_autoarima": mm("AutoARIMA") if "AutoARIMA" in agg.index else None,
    }
    print("SUMMARY_JSON " + json.dumps(summary))

    lines = [
        "# ORÁCULO — Benchmark M4 protocolo AUTO (auto-selección por serie)",
        "",
        f"- Fecha: {pd.Timestamp.now().isoformat(timespec='seconds')}",
        f"- Muestra: {n_used} series M4 mensuales reales · folds={len(FOLD_CUTS)} · h={H}",
        f"- AutoARIMA disponible: {_AUTOARIMA_AVAILABLE}",
        f"- Errores de ajuste: {errors}",
        "",
        "| método | MASE medio | sMAPE medio | OWA |",
        "|---|---|---|---|",
    ]
    for m in agg.index:
        r = agg.loc[m]
        lines.append(f"| {m} | {r['mase']:.4f} | {r['smape']:.2f}% | {r['owa']:.4f} |")
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nReporte: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
