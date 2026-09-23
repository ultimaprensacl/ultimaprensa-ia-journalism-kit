#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Última Prensa - Servidor y Explorador de Datos Datasette
====================================================================
Lanza una instancia de Datasette para auditar, consultar vía SQL y
publicar interactivamente bases de datos periciales (SQLite / DuckDB).

Uso:
    python kit-journalism/scripts/servidor_datasette.py base_datos.db
    python kit-journalism/scripts/servidor_datasette.py base_datos.db --port 8005
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Lanzador de Datasette para bases de datos de investigación de Última Prensa."
    )
    parser.add_argument("database", type=str, help="Ruta al archivo .db o .sqlite")
    parser.add_argument("--port", type=int, default=8005, help="Puerto HTTP (por defecto 8005)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host (por defecto 127.0.0.1)")
    args = parser.parse_args()

    db_path = Path(args.database)
    if not db_path.exists():
        print(f"[!] Error: El archivo de base de datos no existe: {db_path}")
        sys.exit(1)

    print(f"[*] Iniciando Datasette para '{db_path}' en http://{args.host}:{args.port}")
    cmd = [
        sys.executable,
        "-m",
        "datasette",
        "serve",
        str(db_path),
        "-h",
        args.host,
        "-p",
        str(args.port),
        "--cors"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[✓] Servidor Datasette detenido.")


if __name__ == "__main__":
    main()
