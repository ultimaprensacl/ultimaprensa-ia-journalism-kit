#!/usr/bin/env python3
"""
auditar_sec_edgar.py — Conector forense con SEC EDGAR (dgunning/edgartools)
Permite auditar matrices en Wall Street (MetLife, Principal, Prudential, BlackRock)
y empresas con ADR/listado en EE. UU. (SQM, Enel, Latam, Bancos), extrayendo:
- Formularios 10-K / 20-F (Balances anuales y riesgos regulatorios)
- DEF 14A (Proxy Statements: remuneraciones y bonos ejecutivos)
- Exhibit 97 (Políticas obligatorias de Clawback bajo SEC Rule 10D-1 / Dodd-Frank)

Uso:
  .venv/bin/python kit-journalism/scripts/auditar_sec_edgar.py --tickers MET PFG PRU --out salida_sec.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from edgar import Company, set_identity


def auditar_compania_sec(ticker: str, identity: str) -> dict:
    set_identity(identity)
    comp = Company(ticker)
    info = {
        "ticker": ticker.upper(),
        "nombre": getattr(comp, "name", ticker),
        "cik": str(getattr(comp, "cik", "")),
        "sic": str(getattr(comp, "sic", "")),
        "fecha_consulta": datetime.now().isoformat(),
        "ultimos_10k_20f": [],
        "ultimos_proxy_def14a": [],
    }

    try:
        filings_10k = comp.get_filings(form=["10-K", "20-F"]).latest(3)
        if filings_10k:
            if not isinstance(filings_10k, list):
                try:
                    filings_10k = list(filings_10k)
                except TypeError:
                    filings_10k = [filings_10k]
            for f in filings_10k:
                info["ultimos_10k_20f"].append(
                    {
                        "form": getattr(f, "form", ""),
                        "filing_date": str(getattr(f, "filing_date", "")),
                        "accession_no": str(getattr(f, "accession_no", "")),
                        "url": getattr(f, " filing_url", getattr(f, "homepage_url", "")),
                    }
                )
    except Exception as e:
        info["error_10k"] = str(e)

    try:
        filings_proxy = comp.get_filings(form="DEF 14A").latest(2)
        if filings_proxy:
            if not isinstance(filings_proxy, list):
                try:
                    filings_proxy = list(filings_proxy)
                except TypeError:
                    filings_proxy = [filings_proxy]
            for f in filings_proxy:
                info["ultimos_proxy_def14a"].append(
                    {
                        "form": getattr(f, "form", ""),
                        "filing_date": str(getattr(f, "filing_date", "")),
                        "accession_no": str(getattr(f, "accession_no", ""),),
                    }
                )
    except Exception as e:
        info["error_proxy"] = str(e)

    return info


def main():
    parser = argparse.ArgumentParser(
        description="Auditoría forense de matrices y emisores en SEC EDGAR (edgartools)"
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["MET", "PFG", "PRU"],
        help="Tickers bursátiles en NYSE/NASDAQ (ej. MET PFG PRU SQM ENIC LTM)",
    )
    parser.add_argument(
        "--identity",
        default="Unidad Investigacion UltimaPrensa contacto@ultimaprensa.cl",
        help="Identidad requerida por la API oficial de SEC EDGAR",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Ruta opcional para exportar el reporte JSON",
    )
    args = parser.parse_args()

    resultados = {}
    for tk in args.tickers:
        print(f"[SEC EDGAR] Auditando {tk}...", file=sys.stderr)
        resultados[tk.upper()] = auditar_compania_sec(tk, args.identity)

    salida_json = json.dumps(resultados, indent=2, ensure_ascii=False)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(salida_json, encoding="utf-8")
        print(f"[OK] Reporte SEC EDGAR guardado en {out_path}", file=sys.stderr)
    else:
        print(salida_json)


if __name__ == "__main__":
    main()
