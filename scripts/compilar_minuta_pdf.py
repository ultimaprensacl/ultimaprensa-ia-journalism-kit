#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador Institucional de la Minuta Técnica y Estratégica en PDF
Última Prensa - Periodismo de Investigación y Derecho Público
"""

import os
import sys
from pathlib import Path
import pymupdf
from markdown_pdf import MarkdownPdf, Section

CSS_INSTITUCIONAL = """
@page {
    size: A4;
    margin: 48pt 42pt 52pt 42pt;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 9.2pt;
    line-height: 1.55;
    color: #1e293b;
    text-align: justify;
}

h1 {
    color: #0f172a;
    font-size: 15pt;
    font-weight: 800;
    text-align: center;
    letter-spacing: -0.3px;
    margin-top: 10pt;
    margin-bottom: 12pt;
    padding-bottom: 6pt;
    border-bottom: 2.5pt solid #0284c7;
    text-transform: uppercase;
}

h2 {
    color: #1e3a8a;
    font-size: 11.5pt;
    font-weight: 700;
    margin-top: 14pt;
    margin-bottom: 6pt;
    padding-bottom: 3pt;
    border-bottom: 1pt solid #cbd5e1;
    page-break-after: avoid;
}

h3 {
    color: #0369a1;
    font-size: 10pt;
    font-weight: 700;
    margin-top: 10pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 6pt;
}

strong {
    color: #0f172a;
    font-weight: 700;
}

em {
    color: #334155;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0 12pt 0;
    font-size: 8.2pt;
    line-height: 1.4;
}

thead {
    display: table-row-group;
}

tr {
    page-break-inside: avoid;
    page-break-after: auto;
}

th {
    color: #0f172a;
    padding: 6pt 8pt;
    text-align: left;
    font-weight: 800;
    font-size: 8.5pt;
    border-top: 1.5pt solid #0f172a;
    border-bottom: 2pt solid #0f172a;
    border-left: none;
    border-right: none;
    text-transform: uppercase;
}

td {
    padding: 5pt 8pt;
    border: 0.8pt solid #cbd5e1;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #f8fafc;
}

ul, ol {
    margin-top: 2pt;
    margin-bottom: 8pt;
    padding-left: 18pt;
}

li {
    margin-bottom: 3.5pt;
}

blockquote {
    background-color: #f1f5f9;
    border-left: 3.5pt solid #0284c7;
    padding: 6pt 10pt;
    margin: 8pt 0;
    color: #334155;
    font-size: 8.8pt;
    border-radius: 0 4pt 4pt 0;
}

hr {
    border: none;
    border-top: 1pt solid #cbd5e1;
    margin: 12pt 0;
}
"""

def compilar_minuta_pdf(md_path: str, pdf_path: str):
    md_file = Path(md_path)
    pdf_file = Path(pdf_path)
    
    if not md_file.exists():
        raise FileNotFoundError(f"No existe el archivo Markdown: {md_path}")
        
    print(f"[+] Leyendo contenido Markdown: {md_file.resolve()}")
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    # 1. Renderizado base a PDF mediante markdown_pdf
    print("[+] Renderizando HTML/CSS a PDF intermedio...")
    md_pdf = MarkdownPdf(toc_level=2)
    md_pdf.add_section(
        Section(md_text, toc=False, paper_size="A4", borders=(42, 42, -42, -42)),
        user_css=CSS_INSTITUCIONAL
    )
    
    tmp_pdf = f"/tmp/{md_file.stem}_raw.pdf"
    md_pdf.save(tmp_pdf)

    # 2. Post-procesamiento y maquetación con PyMuPDF
    print("[+] Aplicando encabezados, pies de página institucionales y numeración...")
    doc = pymupdf.open(tmp_pdf)
    total_pages = len(doc)
    
    for page_num in range(total_pages):
        page = doc[page_num]
        rect = page.rect # 595.28 x 841.89 (A4)
        
        # Color azul institucional
        c_brand = (0.06, 0.17, 0.36)
        c_gray = (0.35, 0.40, 0.48)
        c_line = (0.80, 0.84, 0.89)
        
        if page_num == 0:
            # Banner superior de carátula / cabecera en Página 1
            page.draw_rect(pymupdf.Rect(42, 28, rect.width - 42, 30), color=c_brand, fill=c_brand)
            page.insert_text(
                pymupdf.Point(42, 22),
                "ÚLTIMA PRENSA  ·  DOSSIER DE INVESTIGACIÓN Y DERECHO PÚBLICO",
                fontsize=7.5,
                fontname="helv",
                color=c_gray
            )
            page.insert_text(
                pymupdf.Point(rect.width - 200, 22),
                "DOCUMENTO TÉCNICO CIUDADANO",
                fontsize=7.5,
                fontname="helv",
                color=c_brand
            )
        else:
            # Encabezado en páginas 2 en adelante
            page.insert_text(
                pymupdf.Point(42, 28),
                "ÚLTIMA PRENSA  |  MINUTA TÉCNICA Y ESTRATÉGICA — CASO RELLENO CURACO",
                fontsize=7.5,
                fontname="helv",
                color=c_brand
            )
            page.draw_line(pymupdf.Point(42, 33), pymupdf.Point(rect.width - 42, 33), color=c_line, width=0.6)

        # Pie de página en todas las páginas
        page.draw_line(pymupdf.Point(42, rect.height - 30), pymupdf.Point(rect.width - 42, rect.height - 30), color=c_line, width=0.6)
        
        texto_pie_izq = "Red Ambiental Ciudadana, Comités APR y Comunidades de la Ruta U-400 · Osorno"
        page.insert_text(
            pymupdf.Point(42, rect.height - 20),
            texto_pie_izq,
            fontsize=7.2,
            fontname="helv",
            color=c_gray
        )
        
        texto_pie_der = f"Página {page_num + 1} de {total_pages}"
        page.insert_text(
            pymupdf.Point(rect.width - 100, rect.height - 20),
            texto_pie_der,
            fontsize=7.5,
            fontname="helv",
            color=c_brand
        )

    # 3. Metadatos del PDF
    doc.set_metadata({
        "title": "Minuta Técnica, Jurídica y Estratégica: Inviabilidad Geotécnica y Ambiental del Relleno Curaco",
        "author": "Pablo Benavides J. - Última Prensa",
        "subject": "Radiografía forense del proyecto Curaco / Centro de Tratamiento Integral y desmontaje del relato oficial",
        "keywords": "Curaco, Osorno, Relleno Sanitario, SMA, SEIA, Corte Suprema, Servitrans, Ciudad Limpia, Medio Ambiente, APR",
        "creator": "Última Prensa Journalism Kit & Open Legal Chile",
        "producer": "PyMuPDF & MarkdownPdf"
    })

    pdf_file.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(pdf_file.resolve()), deflate=True)
    doc.close()
    
    # Limpieza
    if os.path.exists(tmp_pdf):
        os.remove(tmp_pdf)
        
    peso_kb = os.path.getsize(str(pdf_file)) / 1024
    print(f"\n[✓] PDF generado exitosamente:")
    print(f"    - Archivo: {pdf_file.resolve()}")
    print(f"    - Total Páginas: {total_pages}")
    print(f"    - Peso: {peso_kb:.1f} KB\n")

if __name__ == "__main__":
    md_in = "reportajes/caso_relleno_curaco_osorno/minuta_tecnica_ambiental_caso_curaco.md"
    pdf_out = "reportajes/caso_relleno_curaco_osorno/Minuta_Tecnica_Inviabilidad_Curaco_Organizaciones_Ambientales.pdf"
    compilar_minuta_pdf(md_in, pdf_out)
