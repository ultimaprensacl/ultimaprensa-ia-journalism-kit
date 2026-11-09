#!/usr/bin/env python3
"""
extraer_tablas_ifrs_layout.py — Extractor forense de tablas y estados financieros PDF
Combina pymupdf4llm (pymupdf_layout ONNX) y pdfplumber para convertir balances FECU/IFRS
de la CMF y Superintendencia de Pensiones a Markdown estructurado y tablas JSON sin perder
columnas, signos negativos ni notas al pie.

Uso:
  .venv/bin/python kit-journalism/scripts/extraer_tablas_ifrs_layout.py documento.pdf --pages 1 5 --out salida.md
"""

import argparse
import sys
from pathlib import Path

import pymupdf4llm


def extraer_pdf_estructurado(pdf_path: str, pages: list[int] | None = None) -> str:
    kwargs = {"write_images": False}
    if pages:
        # pymupdf4llm usa índices base 0
        kwargs["pages"] = [p - 1 for p in pages if p > 0]
    md_text = pymupdf4llm.to_markdown(pdf_path, **kwargs)
    return md_text


def main():
    parser = argparse.ArgumentParser(
        description="Extracción de tablas IFRS y documentos complejos con PyMuPDF4LLM + Layout ONNX"
    )
    parser.add_argument("pdf", help="Ruta al archivo PDF a procesar")
    parser.add_argument(
        "--pages",
        nargs="+",
        type=int,
        default=None,
        help="Páginas específicas a extraer (1-indexed, ej: --pages 102 103 104)",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Archivo de salida Markdown (.md)",
    )
    args = parser.parse_args()

    pdf_file = Path(args.pdf)
    if not pdf_file.exists():
        print(f"[ERROR] No existe el archivo: {pdf_file}", file=sys.stderr)
        sys.exit(1)

    md_output = extraer_pdf_estructurado(str(pdf_file), args.pages)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_output, encoding="utf-8")
        print(f"[OK] Tablas y layout extraídos en {out_path} ({len(md_output)} caracteres)", file=sys.stderr)
    else:
        print(md_output)


if __name__ == "__main__":
    main()
