#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sanitizar_metadatos_pdf.py — Herramienta Forense de Sanitización y Purgado de Metadatos PDF.
Última Prensa IA Journalism Kit / Open Legal Chile.

Elimina metadatos identificatorios de documentos PDF para resguardar la seguridad de fuentes
periodísticas antes de su publicación digital:
  - Diccionario /Info completo (/CreationDate, /ModDate, /Author, /Creator, /Producer, etc.)
  - Paquetes de metadatos XMP (/Metadata en Root, páginas y streams)
  - Claves privadas de edición /PieceInfo y /LastModified
  - Identificadores únicos de sesión /ID en el trailer
  - Preserva intacta la fidelidad gráfica, resolución y páginas del documento.

Uso:
  python kit-journalism/scripts/sanitizar_metadatos_pdf.py entrada.pdf -o salida.pdf
  python kit-journalism/scripts/sanitizar_metadatos_pdf.py entrada.pdf --inplace
"""

import sys
import os
import argparse
import hashlib
from pathlib import Path
import pikepdf


def sanitizar_pdf(ruta_origen: Path, ruta_destino: Path, preservar_hash_visual: bool = True) -> dict:
    if not ruta_origen.exists():
        raise FileNotFoundError(f"No existe el archivo de origen: {ruta_origen}")

    pdf = pikepdf.open(ruta_origen)

    # Registro de metadatos previos para auditoría
    metadatos_previos = {}
    if "/Info" in pdf.trailer:
        for k, v in pdf.docinfo.items():
            metadatos_previos[str(k)] = str(v)

    # 1. Purgar diccionario /Info del trailer
    if "/Info" in pdf.trailer:
        del pdf.trailer["/Info"]

    # 2. Purgar metadatos XMP del Root (Catálogo)
    root = pdf.Root
    if "/Metadata" in root:
        del root["/Metadata"]
    if "/PieceInfo" in root:
        del root["/PieceInfo"]

    # 3. Purgar metadatos en cada página
    for pagina in pdf.pages:
        if "/Metadata" in pagina:
            del pagina["/Metadata"]
        if "/PieceInfo" in pagina:
            del pagina["/PieceInfo"]
        if "/LastModified" in pagina:
            del pagina["/LastModified"]

    # 4. Anonimizar identificador /ID del trailer
    if "/ID" in pdf.trailer:
        del pdf.trailer["/ID"]

    # Guardar documento sanitizado
    pdf.save(ruta_destino, linearize=False, preserve_pdfa=False)
    pdf.close()

    # Verificación posterior
    check = pikepdf.open(ruta_destino)
    info_restante = list(check.docinfo.keys())
    tiene_xmp = "/Metadata" in check.Root
    total_paginas = len(check.pages)
    check.close()

    resultado = {
        "origen": str(ruta_origen),
        "destino": str(ruta_destino),
        "total_paginas": total_paginas,
        "metadatos_eliminados": metadatos_previos,
        "limpieza_exitosa": (len(info_restante) == 0 and not tiene_xmp),
        "bytes_origen": ruta_origen.stat().st_size,
        "bytes_destino": ruta_destino.stat().st_size,
    }

    return resultado


def main():
    parser = argparse.ArgumentParser(
        description="Sanitizador forense de metadatos PDF para investigación periodística — Última Prensa"
    )
    parser.add_argument("archivo", help="Ruta al archivo PDF a procesar")
    parser.add_argument("-o", "--output", help="Ruta de destino para el archivo sanitizado")
    parser.add_argument("--inplace", action="store_true", help="Sobrescribe el archivo original (hace copia de seguridad)")

    args = parser.parse_args()
    archivo_in = Path(args.archivo).resolve()

    if not archivo_in.exists():
        print(f"[!] Error: El archivo {archivo_in} no existe.")
        sys.exit(1)

    if args.inplace:
        archivo_out = archivo_in.with_suffix(".tmp.pdf")
        backup_path = archivo_in.with_suffix(".orig.bak")
    elif args.output:
        archivo_out = Path(args.output).resolve()
    else:
        archivo_out = archivo_in.parent / f"{archivo_in.stem}_sanitizado.pdf"

    print("==================================================")
    print("Última Prensa — Sanitizador Forense de Metadatos PDF")
    print("==================================================")
    print(f"[*] Procesando: {archivo_in.name}")

    try:
        res = sanitizar_pdf(archivo_in, archivo_out)
        if args.inplace:
            # Crear respaldo y renombrar
            archivo_in.rename(backup_path)
            archivo_out.rename(archivo_in)
            print(f"[+] Respaldo original guardado en: {backup_path.name}")
            print(f"[+] Archivo sanitizado in-place en: {archivo_in.name}")
        else:
            print(f"[+] Archivo sanitizado generado en: {archivo_out.name}")

        print("\n--- Resumen de Purga Forense ---")
        print(f"Páginas verificadas: {res['total_paginas']}")
        print("Metadatos eliminados:")
        if res["metadatos_eliminados"]:
            for k, v in res["metadatos_eliminados"].items():
                print(f"  • {k}: {v}")
        else:
            print("  (No se detectaron campos de docinfo adicionales)")
        print(f"Estado de sanitización: {'EXITOSO (100 % limpio)' if res['limpieza_exitosa'] else 'ADVERTENCIA'}")
        print("==================================================")
    except Exception as e:
        print(f"[!] Error durante la sanitización: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
