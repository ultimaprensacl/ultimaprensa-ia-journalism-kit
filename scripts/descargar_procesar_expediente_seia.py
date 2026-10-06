#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descargador e Ingestador Masivo del Expediente SEIA N° 3675668
(EIA Relleno Sanitario Provincial de Osorno)
"""

import os
import re
import ssl
import time
import json
import html as html_module
import urllib.request
from pathlib import Path
import pymupdf

BASE_DIR = Path("reportajes/caso_caducidad_rca_curaco/expediente_seia_completo")
PDF_DIR = BASE_DIR / "pdfs"
MD_DIR = BASE_DIR / "markdown"

PDF_DIR.mkdir(parents=True, exist_ok=True)
MD_DIR.mkdir(parents=True, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clean_filename(text: str) -> str:
    text = re.sub(r'[^\w\s\.-]', '_', text)
    text = re.sub(r'\s+', '_', text)
    return text.strip('_')[:80]

def fetch_url(url: str, is_binary: bool = False, retries: int = 3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
                if is_binary:
                    return resp.read()
                return resp.read().decode('latin1', errors='ignore')
        except Exception as e:
            time.sleep(1 + attempt)
            if attempt == retries - 1:
                print(f"    [!] Error fetching {url}: {e}")
                return None

print("[1] Consultando tabla oficial de documentos del expediente en e-SEIA...")
xhr_url = "https://seia.sea.gob.cl/expediente/xhr_documentos.php?id_expediente=3675668"
xhr_html = fetch_url(xhr_url)

if not xhr_html:
    print("[-] Error crítico: no se pudo obtener la lista de documentos.")
    exit(1)

rows = re.findall(r'<tr[^>]*>(.*?)</tr>', xhr_html, re.DOTALL | re.IGNORECASE)
print(f"[+] Total de filas detectadas: {len(rows)}")

expediente_data = []

for idx, r in enumerate(rows):
    cols = re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL | re.IGNORECASE)
    if not cols:
        continue
    clean_cols = [re.sub(r'<[^>]+>', '', c).strip() for c in cols]
    link_m = re.search(r'href=[\"\']([^\"\']+)[\"\']', r, re.IGNORECASE)
    href = link_m.group(1) if link_m else ''
    
    # cols format: [N°, N° Doc, Tipo, Descripcion, Origen, Destino, Fecha, ...]
    doc_num = clean_cols[0] if len(clean_cols) > 0 else str(idx)
    doc_id = clean_cols[1] if len(clean_cols) > 1 else ''
    desc = clean_cols[3] if len(clean_cols) > 3 else 'Documento'
    origen = clean_cols[4] if len(clean_cols) > 4 else ''
    destino = clean_cols[5] if len(clean_cols) > 5 else ''
    fecha = clean_cols[6] if len(clean_cols) > 6 else ''
    
    # reformat date DD/MM/YYYY to YYYY-MM-DD
    f_parts = fecha.split('/')
    sort_date = f"{f_parts[2]}-{f_parts[1]}-{f_parts[0]}" if len(f_parts) == 3 else "2009-00-00"
    
    expediente_data.append({
        "num": doc_num,
        "doc_id": doc_id,
        "descripcion": desc,
        "origen": origen,
        "destino": destino,
        "fecha": fecha,
        "sort_date": sort_date,
        "url": href
    })

print(f"[+] Documentos estructurados en el expediente: {len(expediente_data)}")

# Guardar índice en JSON
with open(BASE_DIR / "indice_expediente_seia.json", "w", encoding="utf-8") as f:
    json.dump(expediente_data, f, indent=2, ensure_ascii=False)

# Crear archivo de índice en Markdown
indice_md = [
    "# ÍNDICE DEL EXPEDIENTE SEIA N° 3675668\n",
    "## EIA Relleno Sanitario Provincial de Osorno\n",
    "| N° | Fecha | Documento / Descripción | Emisor / Origen | Destino | Enlace Original |",
    "|:--:|:-----:|:------------------------|:----------------|:--------|:----------------|"
]

for d in expediente_data:
    indice_md.append(f"| {d['num']} | {d['fecha']} | {d['descripcion']} {d['doc_id']} | {d['origen']} | {d['destino']} | [{d['num']}]({d['url']}) |")

with open(BASE_DIR / "INDICE_EXPEDIENTE_SEIA.md", "w", encoding="utf-8") as f:
    f.write("\n".join(indice_md))

print(f"[+] Índice guardado en {BASE_DIR / 'INDICE_EXPEDIENTE_SEIA.md'}")

print("\n[2] Descargando y convirtiendo documentos a Markdown...")

for i, doc in enumerate(expediente_data):
    url = doc["url"]
    if not url or url.startswith('#') or 'modo=iframe' in url:
        continue
    
    # Normalizar URL
    if url.startswith('/'):
        url = f"https://seia.sea.gob.cl{url}"
    elif not url.startswith('http'):
        url = f"https://seia.sea.gob.cl/documentos/{url}"
        
    try:
        doc_num_int = int(doc['num'])
    except ValueError:
        doc_num_int = i + 1
        
    prefix = f"{doc['sort_date']}_DOC_{doc_num_int:02d}_{clean_filename(doc['origen'])}_{clean_filename(doc['descripcion'])}"
    print(f"[{i+1}/{len(expediente_data)}] Doc {doc['num']}: {doc['descripcion'][:40]} ({doc['origen'][:30]})")
    
    # Caso 1: Enlace directo a PDF
    if url.lower().endswith('.pdf'):
        pdf_name = f"{prefix}.pdf"
        md_name = f"{prefix}.md"
        pdf_path = PDF_DIR / pdf_name
        md_path = MD_DIR / md_name
        
        if not md_path.exists():
            pdf_bytes = fetch_url(url, is_binary=True)
            if pdf_bytes:
                with open(pdf_path, "wb") as pf:
                    pf.write(pdf_bytes)
                try:
                    pdf_doc = pymupdf.open(str(pdf_path))
                    text_parts = [f"# {doc['descripcion']}\n\n**Fecha:** {doc['fecha']}  \n**Origen:** {doc['origen']}  \n**Destino:** {doc['destino']}  \n**URL:** {url}\n\n---\n"]
                    for p_num, page in enumerate(pdf_doc):
                        p_txt = page.get_text().strip()
                        if p_txt:
                            text_parts.append(f"## Página {p_num+1}\n\n{p_txt}\n")
                    with open(md_path, "w", encoding="utf-8") as mf:
                        mf.write("\n\n".join(text_parts))
                except Exception as e:
                    print(f"    [!] Error convirtiendo {pdf_name}: {e}")
        continue

    # Caso 2: URL tipo documento.php
    page_html = fetch_url(url)
    if not page_html:
        continue
        
    # Verificar si la página contiene capítulos PDF adjuntos
    pdf_links = re.findall(r'<a[^>]+href=[\"\']([^\"\']+\.pdf[^\'\"]*)[\"\'][^>]*>(.*?)</a>', page_html, re.IGNORECASE)
    
    if pdf_links:
        print(f"    -> Detectados {len(pdf_links)} archivos PDF adjuntos.")
        for sub_url, sub_txt in pdf_links:
            if sub_url.startswith('/'):
                sub_url = f"https://seia.sea.gob.cl{sub_url}"
            sub_title_clean = re.sub(r'<[^>]+>', '', sub_txt).strip()
            sub_title_clean = html_module.unescape(sub_title_clean)
            sub_title = clean_filename(sub_title_clean)
            if not sub_title:
                sub_title = "anexo_pdf"
                
            sub_pdf_name = f"{prefix}_{sub_title}.pdf"
            sub_md_name = f"{prefix}_{sub_title}.md"
            sub_pdf_path = PDF_DIR / sub_pdf_name
            sub_md_path = MD_DIR / sub_md_name
            
            if not sub_md_path.exists():
                sub_bytes = fetch_url(sub_url, is_binary=True)
                if sub_bytes:
                    with open(sub_pdf_path, "wb") as pf:
                        pf.write(sub_bytes)
                    try:
                        p_doc = pymupdf.open(str(sub_pdf_path))
                        p_texts = [f"# {doc['descripcion']} - {sub_title_clean}\n\n**Fecha:** {doc['fecha']}  \n**Origen:** {doc['origen']}  \n**Destino:** {doc['destino']}  \n**URL:** {sub_url}\n\n---\n"]
                        for pn, pg in enumerate(p_doc):
                            pt = pg.get_text().strip()
                            if pt:
                                p_texts.append(f"## Página {pn+1}\n\n{pt}\n")
                        with open(sub_md_path, "w", encoding="utf-8") as mf:
                            mf.write("\n\n".join(p_texts))
                    except Exception as pe:
                        print(f"       [!] Error convirtiendo sub-pdf {sub_pdf_name}: {pe}")
    
    # También procesar el contenido HTML como documento si tiene texto propio
    body_clean = re.sub(r'<script.*?</script>', '', page_html, flags=re.DOTALL | re.IGNORECASE)
    body_clean = re.sub(r'<style.*?</style>', '', body_clean, flags=re.DOTALL | re.IGNORECASE)
    body_clean = html_module.unescape(body_clean)
    
    lines = []
    for line in re.split(r'[\r\n]+', re.sub(r'<br\s*/?>', '\n', body_clean)):
        clean_l = re.sub(r'<[^>]+>', ' ', line).strip()
        clean_l = re.sub(r'\s+', ' ', clean_l)
        if clean_l and not any(k in clean_l for k in ['VER INFORMACI', 'DESCARGAR XML', 'IMPRIMIR', 'Google Tag', 'function()', 'var _gaq']):
            lines.append(clean_l)
            
    # Solo guardar el MD del HTML si tiene contenido sustantivo (más de 15 líneas)
    if len(lines) > 15:
        md_content = f"# {doc['descripcion']}\n\n**Fecha:** {doc['fecha']}  \n**Origen:** {doc['origen']}  \n**Destino:** {doc['destino']}  \n**URL:** {url}\n\n---\n\n" + "\n\n".join(lines)
        md_path = MD_DIR / f"{prefix}.md"
        if not md_path.exists():
            with open(md_path, "w", encoding="utf-8") as mf:
                mf.write(md_content)

print("\n[+] Todos los documentos han sido descargados y procesados a Markdown en:")
print(f"    {MD_DIR.resolve()}")
