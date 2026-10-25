#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
descargar_actas_ulagos.py — Baja las actas del Consejo Superior de la ULagos.

Descarga el listado publicado en la página del Consejo Superior y guarda cada
PDF validándolo: un archivo truncado o una página de error del servidor se
detecta y se reintenta, en vez de quedar como si fuera un acta.

Va de a una conexión, con espera entre peticiones y reintentos con espera
creciente, porque el servidor de la universidad corta la conexión cuando recibe
varias en paralelo (medido: seis descargas simultáneas terminan en HTTP 000 y
dejan archivos de 0 páginas).

Uso:
    python scripts/descargar_actas_ulagos.py --destino "<carpeta>"
    python scripts/descargar_actas_ulagos.py --destino "<carpeta>" --listar

Requisitos: pymupdf (para validar los PDF) y curl.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import pymupdf
except ImportError:  # pragma: no cover
    import fitz as pymupdf  # type: ignore

PAGINA = "https://www.ulagos.cl/acerca-ulagos/presentacion/consejo-superior/"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")


def listar_pdfs() -> list[str]:
    """Extrae los enlaces a PDF de la página del Consejo Superior."""
    proceso = subprocess.run(
        ["curl", "-sSL", "--max-time", "90", "-A", UA, PAGINA],
        capture_output=True, text=True,
    )
    if proceso.returncode != 0 or len(proceso.stdout) < 5000:
        sys.exit(f"No se pudo leer la página del Consejo Superior: {proceso.stderr.strip()[:200]}")
    urls = sorted(set(re.findall(r'https://www\.ulagos\.cl/wp-content/uploads/[^"\']+\.pdf',
                                 proceso.stdout)))
    if not urls:
        sys.exit("La página respondió pero sin enlaces a PDF (¿cambió la estructura?).")
    return urls


def pdf_valido(ruta: Path) -> tuple[bool, int]:
    """Devuelve (válido, páginas). Un PDF truncado se abre con 0 páginas."""
    if not ruta.exists() or ruta.stat().st_size < 2000:
        return False, 0
    try:
        documento = pymupdf.open(ruta)
        paginas = len(documento)
        documento.close()
    except Exception:
        return False, 0
    return paginas > 0, paginas


def descargar(url: str, destino: Path, intentos: int = 3) -> tuple[bool, str]:
    objetivo = destino / Path(urlparse(url).path).name
    detalle = "sin intentos"
    for intento in range(1, max(intentos, 1) + 1):
        proceso = subprocess.run(
            ["curl", "-sSL", "--max-time", "120", "-A", UA,
             "-H", "Referer: " + PAGINA, "-o", str(objetivo), url],
            capture_output=True, text=True,
        )
        valido, paginas = pdf_valido(objetivo)
        if proceso.returncode == 0 and valido:
            return True, f"{paginas} páginas, {objetivo.stat().st_size // 1024} KB"
        detalle = proceso.stderr.strip()[:120] or f"PDF inválido ({paginas} páginas)"
        if intento < intentos:
            time.sleep(5 * intento)
    return False, f"falló tras {intentos} intentos ({detalle})"


def main() -> int:
    parser = argparse.ArgumentParser(description="Descarga de actas del Consejo Superior ULagos")
    parser.add_argument("--destino", required=True, help="carpeta donde guardar los PDF")
    parser.add_argument("--espera", type=float, default=2.0,
                        help="segundos entre peticiones (def: 2)")
    parser.add_argument("--listar", action="store_true", help="solo listar, sin descargar")
    args = parser.parse_args()

    destino = Path(args.destino).expanduser().resolve()
    destino.mkdir(parents=True, exist_ok=True)

    urls = listar_pdfs()
    print(f"Actas publicadas: {len(urls)}")
    if args.listar:
        for url in urls:
            print("  " + url)
        return 0

    nuevos = faltan = 0
    for numero, url in enumerate(urls, 1):
        nombre = Path(urlparse(url).path).name
        objetivo = destino / nombre
        valido, _ = pdf_valido(objetivo)
        if valido:
            continue
        ok, detalle = descargar(url, destino)
        if ok:
            nuevos += 1
            print(f"  [{numero}/{len(urls)}] {nombre}: {detalle}")
        else:
            faltan += 1
            print(f"  [{numero}/{len(urls)}] {nombre}: ERROR {detalle}")
        time.sleep(args.espera)

    print(f"\nDescargadas: {nuevos} · con error: {faltan} · ya estaban: "
          f"{len(urls) - nuevos - faltan}")
    return 0 if faltan == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
