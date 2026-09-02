#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Última Prensa - Compilador de Expedientes y Dossiers Periciales en PDF
====================================================================
Compila escritos de denuncia, reportajes o informes en Markdown junto a
sus anexos documentales en PDF, generando portadas A4 institucionales
para cada anexo y ensamblando un único expediente blindado y foliado.

Uso:
    python compilador_expediente_pdf.py --md escrito.md --salida expediente.pdf
    python compilador_expediente_pdf.py --md escrito.md --anexos config_anexos.json --salida expediente.pdf
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    import pymupdf
    from markdown_pdf import MarkdownPdf, Section
except ImportError:
    print("[-] Error: Dependencias requeridas no encontradas.")
    print("    Instala con: pip install pymupdf markdown-pdf")
    sys.exit(1)


def crear_separador_a4(numero_anexo: str, titulo: str, descripcion: str = "") -> pymupdf.Document:
    """Crea una hoja A4 de separación con diseño sobrio e institucional para el anexo."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)  # Formato A4 estándar
    
    # Barra decorativa superior
    page.draw_rect(pymupdf.Rect(50, 180, 545, 184), color=(0.1, 0.22, 0.4), fill=(0.1, 0.22, 0.4))
    
    # Número de anexo (ej. "ANEXO N° 1")
    page.insert_textbox(
        pymupdf.Rect(50, 120, 545, 170),
        numero_anexo,
        fontsize=24,
        fontname="helv",
        color=(0.06, 0.17, 0.36),
        align=pymupdf.TEXT_ALIGN_CENTER
    )
    
    # Título descriptivo
    page.insert_textbox(
        pymupdf.Rect(50, 210, 545, 290),
        titulo,
        fontsize=14,
        fontname="times-bold",
        color=(0.1, 0.1, 0.1),
        align=pymupdf.TEXT_ALIGN_CENTER
    )
    
    # Descripción y metadatos probatorios
    if descripcion:
        page.insert_textbox(
            pymupdf.Rect(60, 310, 535, 550),
            descripcion,
            fontsize=11,
            fontname="times-roman",
            color=(0.25, 0.25, 0.25),
            align=pymupdf.TEXT_ALIGN_CENTER
        )
        
    return doc


def compilar_expediente(md_path: str, output_path: str, anexos: list = None, version_movil: str = None):
    """
    Compila el documento Markdown y opcionalmente ensambla los PDFs anexos con sus separadores.
    """
    md_file = Path(md_path)
    if not md_file.exists():
        raise FileNotFoundError(f"Archivo Markdown no encontrado: {md_path}")

    print(f"\n[+] Renderizando escrito principal desde: {md_file.name}")
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    # 1. Renderizar escrito principal
    md_pdf = MarkdownPdf(toc_level=0)
    md_pdf.add_section(Section(md_text, toc=False, paper_size="A4", borders=(40, 40, -40, -40)))
    
    tmp_main = f"/tmp/{md_file.stem}_tmp.pdf"
    md_pdf.save(tmp_main)

    if version_movil:
        movil_path = Path(version_movil)
        movil_path.parent.mkdir(parents=True, exist_ok=True)
        md_pdf.save(str(movil_path))
        print(f"[✓] Versión ligera de lectura móvil guardada en: {movil_path}")

    final_doc = pymupdf.open(tmp_main)
    print(f"[+] Escrito principal renderizado: {len(final_doc)} páginas.")

    # 2. Insertar anexos con portadas si existen
    if anexos:
        print(f"[+] Ensamblando {len(anexos)} anexos documentales...")
        for i, item in enumerate(anexos, start=1):
            num = item.get("num", f"ANEXO N° {i}")
            titulo = item.get("title", f"Documento Anexo {i}")
            desc = item.get("desc", "")
            path_doc = item.get("path", "")

            if not path_doc or not os.path.exists(path_doc):
                print(f"[!] Advertencia: Archivo del anexo no encontrado: {path_doc}. Omitiendo.")
                continue

            print(f"    -> Insertando separador y archivo: {num} - {titulo[:45]}...")
            sep_doc = crear_separador_a4(num, titulo, desc)
            final_doc.insert_pdf(sep_doc)
            
            anx_doc = pymupdf.open(path_doc)
            final_doc.insert_pdf(anx_doc)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    final_doc.save(str(out_file))

    size_mb = os.path.getsize(str(out_file)) / (1024 * 1024)
    print(f"[✓] Expediente final compilado con éxito:")
    print(f"    - Destino: {out_file.resolve()}")
    print(f"    - Total páginas: {len(final_doc)}")
    print(f"    - Tamaño: {size_mb:.2f} MB\n")


def main():
    parser = argparse.ArgumentParser(description="Compilador de Expedientes en PDF de Última Prensa.")
    parser.add_argument("--md", required=True, help="Ruta al archivo Markdown principal")
    parser.add_argument("--salida", required=True, help="Ruta del PDF final compilado")
    parser.add_argument("--anexos", help="Ruta a archivo JSON con lista de anexos [{'num', 'title', 'desc', 'path'}]")
    parser.add_argument("--movil", help="Ruta opcional para guardar solo el escrito para lectura móvil")
    args = parser.parse_args()

    anexos_list = []
    if args.anexos:
        with open(args.anexos, "r", encoding="utf-8") as f:
            anexos_list = json.load(f)

    compilar_expediente(args.md, args.salida, anexos_list, args.movil)


if __name__ == "__main__":
    main()
