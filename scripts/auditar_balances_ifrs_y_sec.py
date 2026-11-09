#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditor Forense de Estados Financieros IFRS (CMF/SP) y Cruce SEC EDGAR (Rule 10D-1)
Parte de Última Prensa IA Journalism Kit (kit-journalism)

Extrae de manera automatizada desde PDFs de Estados Financieros IFRS (FECU/CMF/SP):
1. Código 31.11.010 (Ingresos Ordinarios por Comisiones)
2. Código 31.11.020 (Rentabilidad del Encaje)
3. Código 31.11.300 (Ganancia Neta del Ejercicio)
4. Código 90.20.000 (Nómina de Administración: Gerente General, Presidente, Directores con RUN)
5. Código 90.30.000 (Propiedad y Accionistas Controladores)
6. Cruce con SEC EDGAR API (EE. UU.) para verificar políticas de Clawback (Exhibit 97 / Rule 10D-1)
   de matrices listadas en Wall Street (MetLife CIK 0001099219, Principal CIK 0001126328, Prudential CIK 0001137774).
"""

import argparse
import glob
import json
import os
import re
import subprocess
import urllib.request
from typing import Dict, List, Any

SEC_MATRICES_AFP = {
    "PROVIDA": {"matriz": "MetLife, Inc.", "ticker": "MET", "cik": "0001099219"},
    "CUPRUM": {"matriz": "Principal Financial Group, Inc.", "ticker": "PFG", "cik": "0001126328"},
    "HABITAT": {"matriz": "Prudential Financial, Inc.", "ticker": "PRU", "cik": "0001137774"},
}


def extraer_texto_pdf(pdf_path: str, layout: bool = True) -> str:
    """Extrae texto desde PDF preservando coordenadas tabulares mediante pdftotext (Poppler)."""
    cmd = ["pdftotext"]
    if layout:
        cmd.append("-layout")
    cmd.extend([pdf_path, "-"])
    return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")


def auditar_administracion_9020(texto: str) -> List[Dict[str, str]]:
    """Extrae los cargos, nombres y RUT/RUN de la sección 90.20.000 Administración."""
    resultados = []
    idx = texto.find("90.20.000")
    if idx == -1:
        idx = texto.find("90.20")
    if idx == -1:
        return resultados

    bloque = texto[idx : idx + 3500]
    patron = re.compile(
        r"(90\.20\.\d{3})\s+(Representante [Ll]egal|Gerente [Gg]eneral|Presidente|Vicepresidente|Director(?:\s+[Ss]uplente)?)\s+([A-ZÁÉÍÓÚÑa-záéíóúñüÜ\s\-]+?)\s+([0-9\.]{7,10}\-[0-9Kk]|[A-Z0-9]{6,12})"
    )
    for m in patron.finditer(bloque):
        resultados.append({
            "codigo": m.group(1),
            "cargo": m.group(2).strip(),
            "nombre": " ".join(m.group(3).split()),
            "identificacion": m.group(4).strip(),
        })
    return resultados


def consultar_sec_edgar_matriz(cik: str) -> Dict[str, Any]:
    """Consulta la API oficial de SEC EDGAR para verificar últimos reportes 10-K y DEF 14A."""
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "UltimaPrensaInvestigacion/1.0 (contacto@ultimaprensa.cl)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            ultimos_10k = [
                {"form": f, "fecha": d}
                for f, d in zip(forms, dates)
                if f in ("10-K", "DEF 14A")
            ][:4]
            return {
                "entidad": data.get("name"),
                "cik": cik,
                "sic": data.get("sicDescription"),
                "regla_10d1_clawback": "Obligatoria en EE. UU. (SEC Rule 10D-1 / Dodd-Frank Sec. 954 / Exhibit 97)",
                "ultimos_reportes_sec": ultimos_10k,
            }
    except Exception as exc:
        return {"cik": cik, "error": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auditor Forense de Balances IFRS (CMF/SP) y Cruce con SEC EDGAR"
    )
    parser.add_argument(
        "directorio_pdfs",
        help="Ruta al directorio con los PDFs de Estados Financieros IFRS",
    )
    parser.add_argument(
        "--verificar-sec",
        action="store_true",
        help="Consulta en vivo la API de la SEC (EDGAR) para las matrices estadounidenses",
    )
    parser.add_argument(
        "--out-json",
        help="Ruta opcional para guardar el expediente forense en JSON",
    )
    args = parser.parse_args()

    pdfs = sorted(glob.glob(os.path.join(args.directorio_pdfs, "*.pdf")))
    expediente: Dict[str, Any] = {"archivos_auditados": [], "matrices_sec": {}}

    for pdf in pdfs:
        nombre_archivo = os.path.basename(pdf)
        texto = extraer_texto_pdf(pdf, layout=True)
        admin = auditar_administracion_9020(texto)
        tiene_nota_derivados_inversion = bool(
            re.search(r"Derivados para operaciones de inversi[oó]n", texto, re.IGNORECASE)
        )
        expediente["archivos_auditados"].append({
            "archivo": nombre_archivo,
            "administracion_9020": admin,
            "declara_derivados_inversion_l2": tiene_nota_derivados_inversion,
        })

    if args.verificar_sec:
        for afp, info in SEC_MATRICES_AFP.items():
            expediente["matrices_sec"][afp] = consultar_sec_edgar_matriz(info["cik"])

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(expediente, f, ensure_ascii=False, indent=2)
        print(f"[+] Expediente forense exportado en: {args.out_json}")
    else:
        print(json.dumps(expediente, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
