#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Última Prensa - Herramienta de OCR para Sentencias y Dictámenes
====================================================================
Extrae texto mediante OCR neuronal (RapidOCR) desde expedientes PDF
escaneados (CGR, TRICEL, TER, Tribunales de Justicia).

Uso:
    python scripts/ocr_sentencias_pdf.py ruta/al/archivo.pdf salida.txt
"""

import sys
import io
import argparse
from pathlib import Path

try:
    import pypdf
    from rapidocr_onnxruntime import RapidOCR
except ImportError:
    print("[-] Error: Dependencias faltantes.")
    print("    Instala con: pip install pypdf rapidocr_onnxruntime")
    sys.exit(1)


def procesar_ocr(pdf_path: str, output_path: str):
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"[-] Archivo no encontrado: {pdf_path}")
        sys.exit(1)

    print(f"[+] Iniciando procesamiento OCR para: {pdf_file.name}")
    reader = pypdf.PdfReader(str(pdf_file))
    total_paginas = len(reader.pages)
    print(f"[+] Total de páginas detectadas: {total_paginas}")

    ocr = RapidOCR()
    texto_completo = []

    for i, page in enumerate(reader.pages):
        num_pag = i + 1
        print(f"    -> Procesando página {num_pag}/{total_paginas}...", end="\r")
        
        # 1. Intentar extracción de texto nativo
        texto_nativo = page.extract_text() or ""
        if len(texto_nativo.strip()) > 100:
            texto_completo.append(f"=== PÁGINA {num_pag} (Texto Nativo) ===\n{texto_nativo}")
            continue

        # 2. Si es escaneado / imagen, aplicar RapidOCR
        imagenes_pagina = []
        for img_info in page.images:
            if len(img_info.data) < 1000:
                continue
            result, _ = ocr(img_info.data)
            if result:
                lineas = [line[1] for line in result]
                imagenes_pagina.append("\n".join(lineas))
        
        if imagenes_pagina:
            texto_completo.append(f"=== PÁGINA {num_pag} (OCR Neuronal) ===\n" + "\n\n".join(imagenes_pagina))
        else:
            texto_completo.append(f"=== PÁGINA {num_pag} ===\n(Sin texto ni imágenes detectadas)")

    print(f"\n[+] Extracción finalizada con éxito.")
    
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# Extracción OCR - Expediente: {pdf_file.name}\n")
        f.write(f"# Generado por Última Prensa IA Framework\n\n")
        f.write("\n\n".join(texto_completo))

    print(f"[+] Archivo generado en: {out_file.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="OCR para expedientes judiciales y dictámenes públicos.")
    parser.add_argument("pdf", help="Ruta al archivo PDF a procesar")
    parser.add_argument("salida", nargs="?", default="salida_ocr.txt", help="Ruta del archivo de texto de salida")
    args = parser.parse_args()

    procesar_ocr(args.pdf, args.salida)


if __name__ == "__main__":
    main()
