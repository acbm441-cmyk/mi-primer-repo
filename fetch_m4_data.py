# ─────────────────────────────────────────────────────────────────────────────
# ORÁCULO · AACC-PANDHARPUR — descarga de datos reales M4 (competencia oficial)
#
# Formato REAL verificado (OBSERVED 2026-09-02, inspección del archivo):
#   Monthly-train.csv → UNA FILA POR SERIE. V1 = id ("M1".."M48000"),
#   V2..Vn = observaciones (izquierda-alineadas, relleno NaN al final; filas
#   irregulares: ancho de cabecera 2795 ≈ longitud máxima).
#
# 1) Descarga Monthly-train.csv oficial (Mcompetitions/M4-methods) al directorio
#    de datos pesados (fuera de OneDrive).
# 2) Muestra determinista de 60 series mensuales (semilla 42, n>=48) guardada
#    como CSV ancho (columnas=series) en <workspace>/data/m4_monthly_sample.csv.
# Idempotente: si el raw existe, no vuelve a descargar.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.request

import numpy as np
import pandas as pd

URLS = [
    "https://raw.githubusercontent.com/Mcompetitions/M4-methods/master/Dataset/Train/Monthly-train.csv",
    "https://github.com/Mcompetitions/M4-methods/raw/master/Dataset/Train/Monthly-train.csv",
]
DEFAULT_RAW_DIR = r"C:\Users\ACBM\AppData\Local\DEEPSEEK\ORACLE-data\M4"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SAMPLE_OUT = os.path.join(HERE, "data", "m4_monthly_sample.csv")
MIN_LEN = 48
SEED = 42


def download(url: str, dest: str) -> float:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": "oracle-aacc/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as fh:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        t0 = time.time()
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            fh.write(chunk)
            done += len(chunk)
            if total and done % (16 << 20) < (1 << 20):
                print(f"  ... {done / 1e6:7.1f} / {total / 1e6:7.1f} MB "
                      f"({done / max(time.time() - t0, 1e-9) / 1e6:.1f} MB/s)", flush=True)
    os.replace(tmp, dest)
    return done / 1e6


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=60)
    ap.add_argument("--raw-dir", default=DEFAULT_RAW_DIR)
    ap.add_argument("--out", default=DEFAULT_SAMPLE_OUT)
    args = ap.parse_args()

    raw = os.path.join(args.raw_dir, "Monthly-train.csv")
    if not os.path.exists(raw):
        print("Raw no existe, descarga a:", raw, flush=True)
        for url in URLS:
            try:
                size = download(url, raw)
                print("Descarga OK:", url, f"({size:.1f} MB)", flush=True)
                break
            except Exception as exc:  # noqa: BLE001
                print("Fallo:", url, exc, file=sys.stderr)
                part = raw + ".part"
                if os.path.exists(part):
                    os.remove(part)
        else:
            print("ERROR: no se pudo descargar M4", file=sys.stderr)
            return 2
    else:
        print(f"Raw ya presente ({os.path.getsize(raw) / 1e6:.1f} MB), sin descarga", flush=True)

    t0 = time.time()
    # V1 = id de serie (string); V2.. = observaciones
    df = pd.read_csv(raw, header=0, index_col=0)
    print(f"CSV cargado: {df.shape[0]} series x hasta {df.shape[1]} obs "
          f"({time.time() - t0:.1f}s)", flush=True)

    ns = df.notna().sum(axis=1).to_numpy()
    ids = df.index.to_numpy()
    print(f"Longitud media={ns.mean():.0f} min={ns.min()} max={ns.max()} "
          f"| con n>={MIN_LEN}: {int((ns >= MIN_LEN).sum())}", flush=True)

    rng = np.random.default_rng(SEED)
    cand = np.where(ns >= MIN_LEN)[0]
    chosen_idx = rng.choice(cand, size=min(args.sample, len(cand)), replace=False)
    chosen = [str(ids[int(i)]) for i in chosen_idx]

    sub = df.loc[chosen].T  # filas = tiempo, columnas = series
    sub.columns = [str(c) for c in sub.columns]
    maxlen = int(sub.notna().sum(axis=0).max())
    sub = sub.iloc[:maxlen]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    sub.to_csv(args.out, index=False)
    lens = [int(sub[c].notna().sum()) for c in sub.columns]
    print(f"Muestra escrita: {args.out} | series={len(chosen)} "
          f"| longitudes min/max={min(lens)}/{max(lens)}", flush=True)
    print("IDS:", chosen, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
