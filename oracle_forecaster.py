# ─────────────────────────────────────────────────────────────────────────────
# ORÁCULO · AACC-PANDHARPUR — oracle_forecaster (capa 4)
# Módulo reutilizable de pronóstico con escenarios cuantílicos.
#
# PUNTO: ENSEMBLE-AUTO = media simple de Theta (sktime) + AutoETS(auto)
# (sktime/statsmodels) + AutoARIMA (pmdarima); si un componente no ajusta,
# media de los disponibles (se reporta 'used').
#
# INCERTIDUMBRE (etiqueta honesta): intervalo empírico basado en residuales
# in-sample de 1 paso de la familia estadística representativa (ETS add/add/add
# y ARIMA(1,1,1)(0,1,1)12 de statsmodels + naive estacional), σ_pooled = media;
# σ_h = σ_pooled·sqrt(h) (aprox. iid de libro, FPP) y cuantiles gaussianos.
# Limitaciones declaradas: subestima incertidumbre multi-paso y de selección de
# modelo; la calibración empírica real se mide fuera de muestra (validate_m4_oos).
#
# Uso (mensual; periodo estacional 12):
#   from oracle_forecaster import forecast_table, scenarios
#   tabla, meta = forecast_table(train_array, h=18)
#   esc = scenarios(tabla)   # base / upside / downside / tail en el horizonte h
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import numpy as np
import pandas as pd

SEASON = 12
# cuantiles objetivo y sus z gaussianos (simétricos; P50 = punto)
QUANTILES = {0.10: -1.2816, 0.25: -0.6745, 0.50: 0.0,
             0.75: 0.6745, 0.90: 1.2816}


def _period_series(train: np.ndarray) -> pd.Series:
    idx = pd.period_range("1990-01", periods=len(train), freq="M")
    return pd.Series(np.asarray(train, dtype=float), index=idx)


# ── componentes del punto (ENSEMBLE-AUTO) ────────────────────────────────────
def theta_pred(train: np.ndarray, h: int) -> np.ndarray:
    from sktime.forecasting.theta import ThetaForecaster
    fc = ThetaForecaster(sp=SEASON)
    fc.fit(_period_series(train), fh=list(range(1, h + 1)))
    return np.asarray(fc.predict(), dtype=float).ravel()


def autoets_pred(train: np.ndarray, h: int) -> np.ndarray:
    from sktime.forecasting.ets import AutoETS
    fc = AutoETS(auto=True, sp=SEASON, maxiter=1000)
    fc.fit(_period_series(train), fh=list(range(1, h + 1)))
    return np.asarray(fc.predict(), dtype=float).ravel()


def autoarima_pred(train: np.ndarray, h: int) -> np.ndarray:
    from sktime.forecasting.arima import AutoARIMA
    fc = AutoARIMA(sp=SEASON, information_criterion="aic", seasonal=True,
                   stepwise=True, n_jobs=1)
    fc.fit(_period_series(train), fh=list(range(1, h + 1)))
    return np.asarray(fc.predict(), dtype=float).ravel()


COMPONENTS = {"Theta": theta_pred, "AutoETS": autoets_pred,
              "AutoARIMA": autoarima_pred}


def ensemble_auto(train: np.ndarray, h: int,
                  exclude: tuple[str, ...] = ()) -> tuple[np.ndarray, list[str]]:
    """Pronóstico ENSEMBLE-AUTO; devuelve (punto, componentes usados)."""
    preds, used = [], []
    for name, fn in COMPONENTS.items():
        if name in exclude:
            continue
        try:
            p = fn(train, h)
            if p.shape == (h,):
                preds.append(p)
                used.append(name)
        except Exception:  # noqa: BLE001 — robustez por componente
            continue
    if not preds:
        raise RuntimeError("sin componentes disponibles")
    return np.mean(preds, axis=0), used


# ── sigma de la familia representativa (residuales in-sample 1 paso) ─────────
def residual_sigmas(train: np.ndarray) -> dict[str, float]:
    """σ por componente de la familia estadística (statsmodels + naive)."""
    out: dict[str, float] = {}
    y = np.asarray(train, dtype=float)
    dt = pd.Series(y, index=pd.date_range("1990-01-01", periods=len(y), freq="MS"))
    try:
        from statsmodels.tsa.exponential_smoothing.ets import ETSModel
        m = ETSModel(dt, error="add", trend="add", seasonal="add",
                     seasonal_periods=SEASON, initialization_method="estimated")
        out["sigma_ets_fixed"] = float(np.std(m.fit(disp=False).resid))
    except Exception:  # noqa: BLE001
        out["sigma_ets_fixed"] = np.nan
    try:
        from statsmodels.tsa.arima.model import ARIMA
        m = ARIMA(dt, order=(1, 1, 1), seasonal_order=(0, 1, 1, SEASON))
        out["sigma_arima_fixed"] = float(np.std(m.fit().resid))
    except Exception:  # noqa: BLE001
        out["sigma_arima_fixed"] = np.nan
    if len(y) > SEASON:
        out["sigma_snaive"] = float(np.std(np.diff(y[-(4 * SEASON):], n=SEASON)))
    else:
        out["sigma_snaive"] = np.nan
    vals = [v for v in out.values() if np.isfinite(v)]
    out["sigma_pooled"] = float(np.mean(vals)) if vals else np.nan
    return out


# ── tabla de cuantiles y escenarios ──────────────────────────────────────────
def forecast_table(train: np.ndarray, h: int,
                   exclude: tuple[str, ...] = ()) -> tuple[pd.DataFrame, dict]:
    """Devuelve (tabla por horizonte con P10..P90, metadatos auditables)."""
    point, used = ensemble_auto(train, h, exclude=exclude)
    sigmas = residual_sigmas(train)
    sigma = sigmas["sigma_pooled"]
    if not np.isfinite(sigma) or sigma <= 0:
        sigma = float(np.std(np.diff(np.asarray(train, dtype=float)))) or 1.0
    hs = np.arange(1, h + 1, dtype=float)
    half = sigma * np.sqrt(hs)  # σ_h (aprox. iid)
    rows = {"h": hs.astype(int)}
    for q, zq in QUANTILES.items():
        rows[f"P{int(q * 100):02d}"] = point + zq * half
    tab = pd.DataFrame(rows).set_index("h")
    meta = {"components_used": used, "sigma_pooled": sigma,
            "sigmas_by_family": {k: v for k, v in sigmas.items()},
            "interval_method": "gaussiano sobre sigma_pooled*sqrt(h) "
                               "(residuales in-sample 1-paso; etiqueta honesta)"}
    return tab, meta


def scenarios(tab: pd.DataFrame, h_last: int | None = None) -> dict:
    """Escenarios ORACLE en el horizonte elegido (por defecto el último h)."""
    h_last = h_last or int(tab.index[-1])
    row = tab.loc[h_last]
    point = float(row["P50"])
    return {
        "horizon": h_last,
        "base": round(point, 3),
        "upside": round(float(row["P90"]), 3),
        "downside": round(float(row["P10"]), 3),
        "rango_80": (round(float(row["P10"]), 3), round(float(row["P90"]), 3)),
        "rango_50": (round(float(row["P25"]), 3), round(float(row["P75"]), 3)),
    }
