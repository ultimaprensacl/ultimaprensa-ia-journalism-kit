#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Última Prensa - Herramienta de OCR Neuronal con PaddleOCR
====================================================================
Extrae texto de alta precisión mediante PaddleOCR (PP-OCRv4 / Multilingüe)
desde expedientes PDF escaneados, sentencias, contratos públicos y resoluciones.

Uso:
    kit-journalism/.venv-paddle/bin/python kit-journalism/scripts/ocr_paddle.py archivo.pdf [salida.txt] [--force-ocr] [--lang es]
"""

import sys
import os
import argparse
from pathlib import Path
import numpy as np

try:
    import pymupdf  # PyMuPDF
    from PIL import Image
    from paddleocr import PaddleOCR
except ImportError as e:
    print(f"[-] Error: Dependencia faltante: {e}")
    print("    Ejecutar con el entorno virtual Paddle:")
    print("    kit-journalism/.venv-paddle/bin/python kit-journalism/scripts/ocr_paddle.py <archivo.pdf>")
    sys.exit(1)


def procesar_documento_paddle(pdf_path: str, output_path: str = None, lang: str = "es", force_ocr: bool = False):
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"[-] Error: Archivo no encontrado: {pdf_path}")
        sys.exit(1)

    if output_path is None:
        output_path = pdf_file.with_suffix(".txt")
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"[+] Iniciando procesamiento PaddleOCR para: {pdf_file.name}")
    print(f"[+] Idioma: {lang} | Forzar OCR: {force_ocr}")

    doc = pymupdf.open(str(pdf_file))
    total_paginas = len(doc)
    print(f"[+] Total de páginas: {total_paginas}")

    # Inicializar PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang=lang)

    resultado_final = []
    resultado_final.append(f"# TRANSCRIPCIÓN FORENSE OCR - ÚLTIMA PRENSA")
    resultado_final.append(f"# Documento: {pdf_file.name}")
    resultado_final.append(f"# Motor: PaddleOCR (Multilingüe: {lang})")
    resultado_final.append(f"# Total de páginas: {total_paginas}\n")

    for idx, page in enumerate(doc):
        num_pag = idx + 1
        print(f"    -> Procesando página {num_pag}/{total_paginas}...", end="\r")

        # Verificar texto nativo primero si no se fuerza OCR
        texto_nativo = page.get_text() or ""
        if not force_ocr and len(texto_nativo.strip()) > 150:
            resultado_final.append(f"\n=== PÁGINA {num_pag} (Texto Digital Nativo) ===\n")
            resultado_final.append(texto_nativo.strip())
            continue

        # Renderizar página a imagen de alta resolución (200 DPI = matrix 2.08)
        zoom = 200 / 72
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convertir pixmap a numpy array RGB
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.h, pix.w, pix.n))
        
        # Ejecutar PaddleOCR
        result = ocr.ocr(img, cls=True)

        lineas_pagina = []
        if result and len(result) > 0 and result[0] is not None:
            for line in result[0]:
                coords, (texto, confianza) = line
                lineas_pagina.append(texto)

        resultado_final.append(f"\n=== PÁGINA {num_pag} (PaddleOCR - {len(lineas_pagina)} líneas) ===\n")
        if lineas_pagina:
            resultado_final.append("\n".join(lineas_pagina))
        else:
            if len(texto_nativo.strip()) > 0:
                resultado_final.append(texto_nativo.strip())
            else:
                resultado_final.append("(Sin texto detectado en imagen ni capa digital)")

    doc.close()
    print(f"\n[+] OCR finalizado con éxito para {pdf_file.name}")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(resultado_final))

    print(f"[+] Archivo transcrito guardado en: {out_file.resolve()}")
    return out_file


def main():
    parser = argparse.ArgumentParser(description="OCR neuronal con PaddleOCR para Última Prensa.")
    parser.add_argument("pdf", help="Ruta al archivo PDF a procesar")
    parser.add_argument("salida", nargs="?", default=None, help="Ruta de salida del archivo de texto")
    parser.add_argument("--lang", default="es", help="Idioma de reconocimiento (default: es)")
    parser.add_argument("--force-ocr", action="store_true", help="Forzar OCR incluso si hay texto digital nativo")
    args = parser.parse_args()

    procesar_documento_paddle(args.pdf, args.salida, lang=args.lang, force_ocr=args.force_ocr)


if __name__ == "__main__":
    main()
