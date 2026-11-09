#!/usr/bin/env python3
"""
archivar_evidencia_web.py — Preservación forense de evidencia web (estilo Bellingcat)
Extrae el contenido limpio y metadatos de cualquier artículo o fuente web con `trafilatura`,
calcula la huella criptográfica SHA-256 (cadena de custodia pericial Ley 20.886), y
consulta o registra su captura histórica en Internet Archive (Wayback Machine) vía `waybackpy`.

Uso:
  .venv/bin/python kit-journalism/scripts/archivar_evidencia_web.py "https://ejemplo.cl/noticia" --out carpeta_evidencia/
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import trafilatura
from waybackpy import WaybackMachineCDXServerAPI


def archivar_url(url: str, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise RuntimeError(f"No fue posible descargar el contenido de: {url}")

    sha256_raw = hashlib.sha256(downloaded.encode("utf-8", errors="ignore")).hexdigest()
    md_text = trafilatura.extract(
        downloaded,
        output_format="markdown",
        include_links=True,
        include_tables=True,
        with_metadata=True,
    ) or ""

    # Consultar último snapshot en Wayback Machine
    wayback_url = None
    try:
        cdx = WaybackMachineCDXServerAPI(
            url, user_agent="UltimaPrensaForensicArchiver/1.0 (+https://ultimaprensa.cl)"
        )
        newest = cdx.newest()
        if newest:
            wayback_url = newest.archive_url
    except Exception:
        wayback_url = None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    slug = sha256_raw[:12]
    md_path = out_dir / f"evidencia_{slug}.md"
    html_path = out_dir / f"evidencia_{slug}.html"
    meta_path = out_dir / f"evidencia_{slug}_custodia.json"

    html_path.write_text(downloaded, encoding="utf-8", errors="ignore")
    md_path.write_text(md_text, encoding="utf-8")

    custodia = {
        "url_original": url,
        "fecha_captura_utc": timestamp,
        "sha256_html_crudo": sha256_raw,
        "sha256_markdown": hashlib.sha256(md_text.encode("utf-8")).hexdigest(),
        "wayback_machine_snapshot": wayback_url,
        "archivo_html": str(html_path),
        "archivo_markdown": str(md_path),
    }
    meta_path.write_text(json.dumps(custodia, indent=2, ensure_ascii=False), encoding="utf-8")
    return custodia


def main():
    parser = argparse.ArgumentParser(
        description="Archivador forense de fuentes web con SHA-256, Trafilatura y Wayback Machine"
    )
    parser.add_argument("url", help="URL de la noticia, circular o documento web a preservar")
    parser.add_argument(
        "--out",
        default="./evidencia_web",
        help="Directorio donde almacenar el respaldo y acta SHA-256",
    )
    args = parser.parse_args()

    acta = archivar_url(args.url, Path(args.out))
    print(json.dumps(acta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
