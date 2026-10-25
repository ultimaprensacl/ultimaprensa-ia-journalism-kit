#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reocr_actas.py — Re-OCR de expedientes escaneados con Tesseract en español.

El OCR con el que se armó el corpus de ULagos dejó 7.499 acentos rotos en 2,15
millones de caracteres («sesién», «Direccidn», «Rectoria»). Eso no es cosmético:
un buscador de «sesión» no encuentra «sesién», así que el material existe pero es
invisible. Este script rehace el OCR de los PDF sin capa de texto con Tesseract 5
en español a 300 dpi, y deja el resultado en una carpeta aparte para no pisar el
corpus anterior.

Comparación medida en una página de acta (Acta 04/2011, p. 1, 196 palabras):
    Tesseract spa 300dpi → «sesión», «ÁLVAREZ», «ÓSCAR»  (con tildes)
    RapidOCR             → «sesion», «ALVAREZ», «OSCAR»   (sin tildes)

Uso:
    python scripts/reocr_actas.py --entrada "<carpeta>" [--salida <carpeta>] [--dpi 300]
    python scripts/reocr_actas.py --entrada "<carpeta>" --autoprueba

Requisitos:
    tesseract 5 con spa.traineddata (TESSDATA_PREFIX apunta a la carpeta que lo tiene)
    pymupdf
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import pymupdf
except ImportError:  # versiones viejas exponen el módulo como fitz
    import fitz as pymupdf  # type: ignore


def tesseract_disponible() -> tuple[str, str]:
    binario = shutil.which("tesseract")
    if not binario:
        sys.exit("No está instalado tesseract (sudo pacman -S tesseract tesseract-data-spa).")
    entorno = os.environ.copy()
    if not entorno.get("TESSDATA_PREFIX"):
        for candidato in (Path.home() / ".local/share/tessdata", Path("/usr/share/tessdata")):
            if (candidato / "spa.traineddata").exists():
                entorno["TESSDATA_PREFIX"] = str(candidato)
                break
    if not Path(entorno.get("TESSDATA_PREFIX", "/nonexistent") , "spa.traineddata").exists():
        sys.exit("Falta spa.traineddata: descárgalo a ~/.local/share/tessdata")
    return binario, entorno["TESSDATA_PREFIX"]


def tiene_capa_de_texto(pdf: Path) -> bool:
    documento = pymupdf.open(pdf)
    caracteres = sum(len(pagina.get_text()) for pagina in documento)
    paginas = max(len(documento), 1)
    documento.close()
    return caracteres / paginas > 400


def ocr_pagina(imagen: Path, binario: str, tessdata: str, psms: tuple[int, ...] = (3, 6)) -> str:
    """OCR de una página probando varias segmentaciones y quedándose con la que más texto recupera.

    Medido en el Acta 4/2010 p. 2: psm 3 daba 178 palabras y psm 6 daba 212 del
    mismo escaneo. El modo automático perdía texto, y en un expediente lo que
    importa es el recuerdo: si una cláusula no se transcribe, no existe.
    """
    mejor = ""
    for psm in psms:
        proceso = subprocess.run(
            [binario, str(imagen), "stdout", "-l", "spa", "--psm", str(psm)],
            capture_output=True, text=True, env={**os.environ, "TESSDATA_PREFIX": tessdata},
        )
        texto = proceso.stdout.strip()
        if len(texto.split()) > len(mejor.split()):
            mejor = texto
    return mejor


def reocr_pdf(pdf: Path, destino: Path, dpi: int, binario: str, tessdata: str) -> dict:
    documento = pymupdf.open(pdf)
    salida, escritos = [], 0
    for numero, pagina in enumerate(documento, start=1):
        imagen = destino.parent / f".tmp_{pdf.stem}_{numero}.png"
        pagina.get_pixmap(dpi=dpi).save(imagen)
        texto = ocr_pagina(imagen, binario, tessdata)
        if texto:
            salida.append(f"\n=== PÁGINA {numero} ===\n{texto}")
            escritos += 1
        imagen.unlink(missing_ok=True)
    documento.close()
    if salida:
        destino.write_text("\n".join(salida) + "\n", encoding="utf-8")
    return {"pdf": pdf.name, "paginas": len(salida), "escritas": escritos,
            "caracteres": sum(len(s) for s in salida)}


def medir(texto: str) -> tuple[int, int]:
    """Devuelve (palabras, patrones de acento roto)."""
    palabras = len(texto.split())
    rotos = len(re.findall(r"(sién|cién|dén\b|idn\b|acién|Rectoria|\bafio\b|\bano\b)", texto))
    return palabras, rotos


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-OCR de actas escaneadas con Tesseract español")
    parser.add_argument("--entrada", required=True, help="carpeta con los PDF")
    parser.add_argument("--salida", help="carpeta destino (por defecto, <entrada>/texto_ocr_v2)")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--forzar", action="store_true", help="rehacer los que ya existen")
    args = parser.parse_args()

    binario, tessdata = tesseract_disponible()
    entrada = Path(args.entrada).resolve()
    salida = Path(args.salida).resolve() if args.salida else entrada / "texto_ocr_v2"
    salida.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(entrada.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No hay PDF en {entrada}")

    inicio = time.time()
    hechos = omitidos = 0
    for pdf in pdfs:
        destino = salida / f"{pdf.stem}.txt"
        if destino.exists() and not args.forzar:
            omitidos += 1
            continue
        if tiene_capa_de_texto(pdf):
            # Con capa de texto nativa no hace falta OCR: se extrae directo.
            documento = pymupdf.open(pdf)
            texto = "\n".join(pagina.get_text() for pagina in documento)
            documento.close()
            destino.write_text(texto, encoding="utf-8")
            print(f"  [texto nativo] {pdf.name}")
        else:
            resumen = reocr_pdf(pdf, destino, args.dpi, binario, tessdata)
            print(f"  [ocr] {pdf.name}: {resumen['paginas']} páginas, {resumen['caracteres']:,} caracteres")
        hechos += 1

    total_palabras = total_rotos = 0
    for archivo in salida.glob("*.txt"):
        palabras, rotos = medir(archivo.read_text(encoding="utf-8", errors="ignore"))
        total_palabras += palabras
        total_rotos += rotos
    print(f"\nListo en {time.time() - inicio:.0f}s · {hechos} procesados, {omitidos} ya existían")
    print(f"Corpus nuevo: {total_palabras:,} palabras · {total_rotos} patrones de acento roto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
