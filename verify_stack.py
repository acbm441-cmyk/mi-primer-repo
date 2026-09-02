# ─────────────────────────────────────────────────────────────────────────────
# ORÁCULO — esqueleto ejecutable del ecosistema AACC-PANDHARPUR
# Stack Python alineado con fpppy (Forecasting: Principles and Practice, ed. Python)
# Core: statsmodels + scikit-learn + sktime  ·  Python 3.14.7
#
# Verificación real de métodos M4/M5-style: ejecuta ajuste + pronóstico + error
# sobre series sintéticas deterministas (semilla fija). NO es un benchmark
# científico: es una prueba de que el esqueleto corre (smoke/verification test).
#
# Notas de API verificadas contra sktime 1.1.0 / statsmodels 0.15.0 / sklearn 1.7.2
# (OBSERVED 2026-09-02, vía sondas de ejecución real):
#  - sktime exige PeriodIndex para ThetaForecaster/NaiveForecaster.
#  - Naive estacional en sktime 1.x: NaiveForecaster(strategy="last", sp=k).
#  - Reducción M5: sktime.forecasting.compose.RecursiveTabularRegressionForecaster
#    (parámetro estimator=; módulo sktime.forecasting.reduced ya no existe).
#  - HistGradientBoostingRegressor NO ejecuta dentro del sandbox DSH (intenta
#    crear pipes/threads bloqueados); GradientBoostingRegressor clásico sí.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import platform
import sys
import time

import numpy as np
import pandas as pd

# ── núcleo del stack (si falta, la verificación debe fallar claro) ───────────
import sklearn  # noqa: F401
import statsmodels  # noqa: F401
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.exponential_smoothing.ets import ETSModel

REPORT = "verify_stack_report.md"
ROWS: list[list[str]] = []
FAILURES: list[str] = []


def run_case(name: str, fn) -> str:
    """Ejecuta un caso real; devuelve PASS/FAIL con duración y mensaje."""
    t0 = time.time()
    try:
        out = fn()
        dt = time.time() - t0
        print(f"  [PASS] {name}  ({dt:.1f}s) {out}")
        return f"PASS ({dt:.1f}s)"
    except Exception as exc:  # noqa: BLE001 — la verificación captura todo
        dt = time.time() - t0
        msg = f"{type(exc).__name__}: {exc}"
        print(f"  [FAIL] {name}  ({dt:.1f}s) {msg}")
        FAILURES.append(f"{name}: {msg}")
        return f"FAIL ({dt:.1f}s)"


# ── métricas M4-style calculadas a mano (sin dependencia de API) ─────────────
def mae(a, b) -> float:
    return float(np.mean(np.abs(np.asarray(a) - np.asarray(b))))


def rmse(a, b) -> float:
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def smape(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.mean(200.0 * np.abs(a - b) / (np.abs(a) + np.abs(b))))


def mase(y_train, a, b, season: int) -> float:
    """MASE: MAE(test) / MAE(naive estacional en entrenamiento)."""
    yt = np.asarray(y_train, float)
    naive_err = np.mean(np.abs(yt[season:] - yt[:-season])) if len(yt) > season else np.nan
    if not naive_err or np.isnan(naive_err):
        return float("nan")
    return mae(a, b) / float(naive_err)


# ── series sintéticas deterministas sobre PeriodIndex ────────────────────────
def make_monthly(n: int = 96, seed: int = 7) -> pd.Series:
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=float)
    y = (50.0 + 0.35 * t + 12.0 * np.sin(2 * np.pi * t / 12)
         + rng.normal(0.0, 1.6, size=n))
    idx = pd.period_range("2020-01", periods=n, freq="M")
    return pd.Series(y, index=idx)


def make_weekly(n: int = 130, seed: int = 123) -> tuple[pd.Series, np.ndarray]:
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=float)
    promo = (rng.random(n) < 0.25).astype(float)
    y = (30 + 6 * np.sin(2 * np.pi * t / 52) + 8.0 * promo
         + rng.normal(0.0, 1.4, size=n))
    idx = pd.period_range("2022-01-03", periods=n, freq="W-MON")
    return pd.Series(y, index=idx), promo


def sktime_forecast(fc, train: pd.Series, fh: list[int],
                    X_train: pd.DataFrame | None = None,
                    X_test: pd.DataFrame | None = None) -> np.ndarray:
    """Ajusta y predice con un forecaster de sktime (patrón verificado)."""
    if X_train is not None:
        fc.fit(train, X=X_train, fh=fh)
        pred = fc.predict(X=X_test)
    else:
        fc.fit(train, fh=fh)
        pred = fc.predict()
    return np.asarray(pred, dtype=float).ravel()


def append_row(label: str, test: np.ndarray, pred: np.ndarray,
               train: np.ndarray, season: int) -> None:
    ROWS.append([label, f"{mae(test, pred):.3f}", f"{rmse(test, pred):.3f}",
                 f"{mase(train, test, pred, season):.3f}", f"{smape(test, pred):.2f}%"])


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN A — M4-style: Theta, SeasonalNaive, ETS, ARIMA (h=12)
# ═════════════════════════════════════════════════════════════════════════════
def section_m4() -> None:
    print("\n## A) M4-style — univariado h=12, 84 obs train / 12 test")
    from sktime.forecasting.naive import NaiveForecaster
    from sktime.forecasting.theta import ThetaForecaster

    y = make_monthly(96, seed=7)
    train_p, test_p = y.iloc[:84], y.iloc[84:]
    fh = list(range(1, 13))

    def _theta():
        p = sktime_forecast(ThetaForecaster(sp=12), train_p, fh)
        append_row("Theta (sktime)", test_p.values, p, train_p.values, 12)
        return f"MAE={mae(test_p.values, p):.3f}"
    run_case("Theta (sktime)", _theta)

    def _snaive():
        p = sktime_forecast(NaiveForecaster(strategy="last", sp=12), train_p, fh)
        append_row("SeasonalNaive sp12 (sktime)", test_p.values, p, train_p.values, 12)
        return f"MAE={mae(test_p.values, p):.3f}"
    run_case("SeasonalNaive sp12 (sktime)", _snaive)

    def _ets():
        # statsmodels ETS sobre DatetimeIndex (derivado del PeriodIndex)
        train_dt = pd.Series(train_p.values, index=train_p.index.to_timestamp())
        test_dt = pd.Series(test_p.values, index=test_p.index.to_timestamp())
        model = ETSModel(train_dt, error="add", trend="add", seasonal="add",
                         seasonal_periods=12, initialization_method="estimated")
        res = model.fit(disp=False)
        p = np.asarray(res.forecast(12)).ravel()
        append_row("ETS add/add/add (statsmodels)", test_p.values, p, train_p.values, 12)
        return f"MAE={mae(test_p.values, p):.3f}"
    run_case("ETS (statsmodels)", _ets)

    def _arima():
        train_dt = pd.Series(train_p.values, index=train_p.index.to_timestamp())
        test_dt = pd.Series(test_p.values, index=test_p.index.to_timestamp())
        model = ARIMA(train_dt, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12))
        res = model.fit()
        p = np.asarray(res.forecast(12)).ravel()
        append_row("ARIMA(1,1,1)(0,1,1)12 (statsmodels)", test_p.values, p,
                   train_p.values, 12)
        return f"MAE={mae(test_p.values, p):.3f}"
    run_case("ARIMA (statsmodels)", _arima)


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN B — M5-style: reducción ML (sktime + sklearn) con exógena promo
# ═════════════════════════════════════════════════════════════════════════════
def section_m5() -> None:
    print("\n## B) M5-style — reducción recursiva GBR lag8 + exógena promo (h=12)")
    from sktime.forecasting.compose import RecursiveTabularRegressionForecaster
    from sktime.forecasting.naive import NaiveForecaster
    from sklearn.ensemble import GradientBoostingRegressor

    s, promo = make_weekly(130, seed=123)
    train_p, test_p = s.iloc[:118], s.iloc[118:]
    fh = list(range(1, 13))
    X_all = pd.DataFrame({"promo": promo}, index=s.index)

    def _gb_reduction():
        fc = RecursiveTabularRegressionForecaster(
            estimator=GradientBoostingRegressor(random_state=42), window_length=8)
        p = sktime_forecast(fc, train_p, fh, X_train=X_all.iloc[:118],
                            X_test=X_all.iloc[118:])
        append_row("Reduction GBR lag8+promo (sktime+sklearn)", test_p.values, p,
                   train_p.values, 52)
        return f"MAE={mae(test_p.values, p):.3f}"
    run_case("M5 reduction ML (sktime+sklearn)", _gb_reduction)

    def _sn_bench():
        p = sktime_forecast(NaiveForecaster(strategy="last", sp=52), train_p, fh)
        append_row("SeasonalNaive sp52 (benchmark)", test_p.values, p,
                   train_p.values, 52)
        return f"MAE={mae(test_p.values, p):.3f}"
    run_case("M5 naive benchmark (sktime)", _sn_bench)


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN C — toolchain probabilística: P(EVENTO|EVIDENCIA) calibrada
# ═════════════════════════════════════════════════════════════════════════════
def section_calibration() -> None:
    print("\n## C) Calibración probabilística (scikit-learn) — P(evento|X)")
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import brier_score_loss
    from sklearn.model_selection import train_test_split

    def _brier():
        rng = np.random.default_rng(2026)
        X = rng.normal(size=(800, 3))
        logit = 0.6 * X[:, 0] - 0.4 * X[:, 1] + 0.2 * X[:, 2]
        y = (rng.random(800) < 1 / (1 + np.exp(-logit))).astype(int)
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=1)
        cal = CalibratedClassifierCV(LogisticRegression(max_iter=2000),
                                     method="isotonic", cv=5)
        cal.fit(Xtr, ytr)
        proba = cal.predict_proba(Xte)[:, 1]
        bs = brier_score_loss(yte, proba)
        ROWS.append(["CalibratedClassifierCV isotonic", f"Brier={bs:.4f}", "", "", ""])
        return f"Brier={bs:.4f} (<0.25 = razonable)"
    run_case("Calibración isotónica (sklearn)", _brier)


# ═════════════════════════════════════════════════════════════════════════════
def main() -> int:
    print("=" * 78)
    print("ORÁCULO — verificación real del stack Python (fpppy-aligned)")
    print("=" * 78)
    import json
    import scipy
    import sktime
    import matplotlib
    versions = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "statsmodels": statsmodels.__version__,
        "scikit-learn": sklearn.__version__,
        "sktime": sktime.__version__,
        "matplotlib": matplotlib.__version__,
    }
    print(" | ".join(f"{k}={v}" for k, v in versions.items()))

    section_m4()
    section_m5()
    section_calibration()

    head = ["método", "MAE", "RMSE", "MASE", "sMAPE"]
    lines = [
        "# ORÁCULO — verificación del stack (reporte generado)",
        "",
        f"- Fecha: {pd.Timestamp.now().isoformat(timespec='seconds')}",
        f"- Python: {platform.python_version()} · ejecutable: {sys.executable}",
        f"- Versiones: {json.dumps(versions)}",
        "",
        "| " + " | ".join(head) + " |",
        "|" + "---|" * len(head),
    ]
    for row in ROWS:
        padded = row + [""] * (len(head) - len(row))
        lines.append("| " + " | ".join(padded[:len(head)]) + " |")
    lines += ["", f"**Casos fallidos: {len(FAILURES)}**"]
    if FAILURES:
        lines += ["- " + f for f in FAILURES]
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nReporte escrito en {REPORT}")
    print(f"RESULTADO: {'OK' if not FAILURES else f'{len(FAILURES)} FALLO(S)'}")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
