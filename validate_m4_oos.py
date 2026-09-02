# ─────────────────────────────────────────────────────────────────────────────
# ORÁCULO · AACC-PANDHARPUR — validación FUERA DE MUESTRA contra el test
# oficial de M4 (capa 4)
#
# Para cada serie de la muestra determinista (60, semilla 42):
#   1) ENSEMBLE-AUTO (oracle_forecaster) ajustado SOLO sobre el train oficial
#   2) pronóstico h=18 + intervalos P10..P90 (gaussiano empírico, σ√h)
#   3) comparación contra los 18 valores REALES del test oficial M4 (holdout
#      jamás usado en desarrollo): MAE/MASE/sMAPE y COBERTURA empírica del
#      intervalo nominal-80% (P10-P90).
# Reporte: m4_oos_validation_report.md · resultados: m4_oos_validation.csv
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

from verify_stack import mae, smape, mase
from oracle_forecaster import forecast_table

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN_CSV = os.path.join(HERE, "data", "m4_monthly_sample.csv")
TEST_CSV = r"C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-data\M4\Monthly-test.csv"
REPORT = os.path.join(HERE, "m4_oos_validation_report.md")
OUT_CSV = os.path.join(HERE, "m4_oos_validation.csv")
H = 18
SEASON = 12


def main() -> int:
    train = pd.read_csv(TRAIN_CSV)
    test = pd.read_csv(TEST_CSV, header=0, index_col=0)
    print("test shape:", test.shape, "| cols head:", list(test.columns[:4]))

    rows: list[dict] = []
    n_used = 0
    t0 = time.time()
    for col in train.columns:
        y = train[col].dropna().to_numpy(dtype=float)
        if len(y) < H + SEASON:
            continue
        try:
            actuals = test.loc[col].dropna().to_numpy(dtype=float)[:H]
        except KeyError:
            print(f"  [warn] id {col} no está en el test oficial", flush=True)
            continue
        if len(actuals) < H:
            continue
        n_used += 1
        try:
            tab, meta = forecast_table(y, H)
            p = tab["P50"].to_numpy()
            p10 = tab["P10"].to_numpy()
            p90 = tab["P90"].to_numpy()
        except Exception as exc:  # noqa: BLE001
            print(f"  [warn] {col}: {exc}", flush=True)
            continue
        hits = int(np.sum((actuals >= p10) & (actuals <= p90)))
        rows.append({
            "series": col, "n_train": len(y),
            "components": "+".join(meta["components_used"]),
            "mae": mae(actuals, p), "mase": mase(y, actuals, p, SEASON),
            "smape": smape(actuals, p), "hits_80": hits,
            "sigma_pooled": meta["sigma_pooled"],
        })
        if n_used % 10 == 0:
            print(f"  ... {n_used} series ({time.time() - t0:.0f}s)", flush=True)

    if not rows:
        print("ERROR: sin series validables", file=sys.stderr)
        return 1
    res = pd.DataFrame(rows)
    res.to_csv(OUT_CSV, index=False)

    tot_pts = int(len(res) * H)
    coverage = float(res["hits_80"].sum()) / tot_pts
    summary = {
        "n_series": int(len(res)), "n_points": tot_pts,
        "mase_mean": float(res["mase"].mean()),
        "smape_mean": float(res["smape"].mean()),
        "mae_mean": float(res["mae"].mean()),
        "coverage_nominal80": coverage,
        "n_hits": int(res["hits_80"].sum()),
        "pct_worse_than_naive": float((res["mase"] > 1.0).mean()),
    }
    print("SUMMARY_JSON " + json.dumps(summary))
    print("coverage nominal 80% ->", f"{coverage:.1%}",
          f"({summary['n_hits']}/{tot_pts})")
    print("MASE medio OOS:", f"{summary['mase_mean']:.4f}",
          "| sMAPE:", f"{summary['smape_mean']:.2f}%")

    lines = [
        "# ORACULO - Validacion OOS vs test oficial M4 (capa 4)",
        "",
        f"- Fecha: {pd.Timestamp.now().isoformat(timespec='seconds')}",
        f"- Metodo: ENSEMBLE-AUTO (Theta+AutoETS+AutoARIMA) + intervalos "
        f"gaussianos empiricos (sigma_pooled*sqrt(h))",
        f"- Series: {len(res)} (test oficial jamas usado en desarrollo) "
        f"x h={H} = {tot_pts} puntos OOS",
        "",
        "| metrica | valor |",
        "|---|---|",
        f"| MASE medio OOS | {summary['mase_mean']:.4f} |",
        f"| sMAPE medio OOS | {summary['smape_mean']:.2f}% |",
        f"| MAE medio OOS | {summary['mae_mean']:.3f} |",
        f"| cobertura nominal 80% (P10-P90) | {coverage:.1%} "
        f"({summary['n_hits']}/{tot_pts}) |",
        f"| series con MASE>1 (peor que naive) | {summary['pct_worse_than_naive']:.1%} |",
        "",
        "Notas epistemicas: intervalos basados en sigma_pooled (familia "
        "ETS/ARIMA/naive) con aproximacion iid sqrt(h) - la cobertura empirica "
        "mide su calibracion real. Si coverage >> 80%, los intervalos son "
        "conservadores (sobre-anchos); si < 80%, subestiman incertidumbre.",
    ]
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("Reporte:", REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
