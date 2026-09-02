#!/usr/bin/env python3
"""
ingestar_documentos_md.py - Última Prensa Journalism Kit
Convierte automáticamente documentos (PDF, DOCX, XLSX, imágenes) a Markdown
estructurado para facilitar el análisis pericial, fact-checking y redacción.
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def convert_with_markitdown(file_path: Path) -> str:
    """Convierte un archivo usando la librería MarkItDown de Microsoft."""
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(str(file_path))
        return result.text_content
    except Exception as e:
        print(f"[!] Error con MarkItDown en {file_path.name}: {e}")
        return ""

def convert_with_poppler(file_path: Path) -> str:
    """Fallback con pdftotext para PDFs complejos."""
    try:
        res = subprocess.check_output(["pdftotext", "-layout", str(file_path), "-"], stderr=subprocess.DEVNULL)
        return res.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[!] Error con pdftotext en {file_path.name}: {e}")
        return ""

def convert_with_ocr(file_path: Path) -> str:
    """OCR con Tesseract para documentos escaneados o imágenes."""
    try:
        out_base = f"/tmp/ocr_{file_path.stem}"
        subprocess.run(["tesseract", str(file_path), out_base, "-l", "spa+eng"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(f"{out_base}.txt", "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except Exception as e:
        print(f"[!] Error con Tesseract OCR en {file_path.name}: {e}")
        return ""

def process_file(file_path: Path, output_dir: Path, force_ocr: bool = False):
    """Procesa un archivo individual y lo guarda como Markdown."""
    ext = file_path.suffix.lower()
    print(f"[*] Procesando: {file_path.name}...")
    
    content = ""
    if force_ocr or ext in [".png", ".jpg", ".jpeg", ".webp"]:
        content = convert_with_ocr(file_path)
    else:
        content = convert_with_markitdown(file_path)
        if not content.strip() and ext == ".pdf":
            print(f"[*] Intentando con pdftotext para: {file_path.name}...")
            content = convert_with_poppler(file_path)
        if not content.strip() and ext == ".pdf":
            print(f"[*] PDF sin texto digital. Aplicando OCR a: {file_path.name}...")
            content = convert_with_ocr(file_path)

    if not content.strip():
        print(f"[X] No se pudo extraer contenido de: {file_path.name}")
        return None

    # Header con metadatos del documento
    md_header = f"""---
documento_origen: "{file_path.name}"
tamano_bytes: {file_path.stat().st_size}
fecha_extraccion: "{Path(file_path).stat().st_mtime}"
formato_original: "{ext}"
---

# Transcripción Estructurada: {file_path.stem}

{content}
"""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{file_path.stem}.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md_header)
    
    print(f"[✓] Markdown guardado en: {out_file}")
    return out_file

def main():
    parser = argparse.ArgumentParser(description="Convierte documentos periciales a Markdown para Última Prensa")
    parser.add_argument("--dir", type=str, help="Directorio con documentos a procesar")
    parser.add_argument("--file", type=str, help="Archivo específico a procesar")
    parser.add_argument("--out", type=str, default="notas_y_datos/documentos_md", help="Directorio de salida para los .md")
    parser.add_argument("--ocr", action="store_true", help="Forzar OCR con Tesseract")
    args = parser.parse_args()

    out_path = Path(args.out)

    if args.file:
        f = Path(args.file)
        if not f.exists():
            print(f"[X] Archivo no encontrado: {f}")
            sys.exit(1)
        process_file(f, out_path, force_ocr=args.ocr)
    elif args.dir:
        d = Path(args.dir)
        if not d.exists() or not d.is_dir():
            print(f"[X] Directorio no encontrado: {d}")
            sys.exit(1)
        
        valid_exts = [".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg", ".jpeg", ".txt"]
        files = [p for p in d.iterdir() if p.suffix.lower() in valid_exts]
        print(f"[*] Encontrados {len(files)} documentos en {d}")
        
        for f in sorted(files):
            process_file(f, out_path, force_ocr=args.ocr)
    else:
        print("[!] Debes especificar --dir o --file. Usa --help para ver opciones.")
        sys.exit(1)

if __name__ == "__main__":
    main()
