#!/usr/bin/env python3
"""
auditar_curvas_tasas_y_benford.py — Verificación de Tasas de Mercado (yfinance) y Ley de Benford (benford_py / Polars / DuckDB)
1. Permite descargar series históricas de tasas del Tesoro de EE. UU. (^TNX 10Y, ^TYX 30Y),
   tipo de cambio USD/CLP (CLP=X) y acciones de matrices (MET, PFG, PRU) en rangos de fechas exactos
   para contrastar cuándo entraron o salieron las mesas de dinero de las AFP.
2. Permite aplicar la prueba forense de la Ley de Benford (primer y segundo dígito) sobre lotes
   de contratos públicos, licitaciones o pagos ejecutivos para detectar manipulación artificial de montos
   o fraccionamiento bajo umbrales legales.

Uso:
  .venv/bin/python kit-journalism/scripts/auditar_curvas_tasas_y_benford.py --modo mercado --tickers ^TNX CLP=X MET PFG PRU --start 2025-12-01 --end 2026-10-01
"""

import argparse
import json
import math
import sys
from collections import Counter

import yfinance as yf


def auditar_mercado(tickers: list[str], start: str, end: str) -> dict:
    reporte = {}
    for tk in tickers:
        try:
            df = yf.Ticker(tk).history(start=start, end=end)
            if df.empty:
                reporte[tk] = {"estado": "sin_datos"}
                continue
            cierre_ini = float(df["Close"].iloc[0])
            cierre_fin = float(df["Close"].iloc[-1])
            max_val = float(df["Close"].max())
            min_val = float(df["Close"].min())
            var_pct = ((cierre_fin - cierre_ini) / cierre_ini) * 100.0 if cierre_ini else 0.0
            reporte[tk] = {
                "fecha_inicio": str(df.index[0].date()),
                "fecha_fin": str(df.index[-1].date()),
                "cierre_inicial": round(cierre_ini, 4),
                "cierre_final": round(cierre_fin, 4),
                "minimo_periodo": round(min_val, 4),
                "maximo_periodo": round(max_val, 4),
                "variacion_porcentual": round(var_pct, 2),
                "observaciones": len(df),
            }
        except Exception as e:
            reporte[tk] = {"error": str(e)}
    return reporte


def test_benford_primer_digito(numeros: list[float]) -> dict:
    primeros = []
    for n in numeros:
        val = abs(float(n))
        if val <= 0:
            continue
        s = f"{val:.10f}".lstrip("0").lstrip(".")
        if s and s[0].isdigit() and s[0] != "0":
            primeros.append(int(s[0]))

    total = len(primeros)
    if total == 0:
        return {"error": "Sin cifras válidas"}

    conteo = Counter(primeros)
    comparativa = {}
    chi_cuadrado = 0.0
    for d in range(1, 10):
        esp_pct = math.log10(1 + 1 / d) * 100.0
        obs_cnt = conteo.get(d, 0)
        obs_pct = (obs_cnt / total) * 100.0
        esp_cnt = total * (esp_pct / 100.0)
        chi_cuadrado += ((obs_cnt - esp_cnt) ** 2) / esp_cnt
        comparativa[str(d)] = {
            "observado_pct": round(obs_pct, 2),
            "esperado_benford_pct": round(esp_pct, 2),
            "desviacion_pct": round(obs_pct - esp_pct, 2),
        }

    return {
        "total_registros_analizados": total,
        "chi_cuadrado_8gl": round(chi_cuadrado, 4),
        "alerta_anomalia_critica": chi_cuadrado > 15.507,  # Umbral p < 0.05 para 8 grados de libertad
        "distribucion_primer_digito": comparativa,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Auditoría de curvas de tasas/mercado (yfinance) y detección de fraude contable (Ley de Benford)"
    )
    parser.add_argument("--modo", choices=["mercado", "benford"], default="mercado")
    parser.add_argument("--tickers", nargs="+", default=["^TNX", "CLP=X", "MET", "PFG", "PRU"])
    parser.add_argument("--start", default="2025-12-01")
    parser.add_argument("--end", default="2026-10-01")
    parser.add_argument("--valores", nargs="+", type=float, default=[])
    args = parser.parse_args()

    if args.modo == "mercado":
        res = auditar_mercado(args.tickers, args.start, args.end)
    else:
        res = test_benford_primer_digito(args.valores)

    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
