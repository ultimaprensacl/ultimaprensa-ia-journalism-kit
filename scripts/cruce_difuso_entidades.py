#!/usr/bin/env python3
"""
cruce_difuso_entidades.py — Cruce difuso y resolución de entidades (RapidFuzz + RecordLinkage + FollowTheMoney)
Cruza nóminas de directores y gerentes (ej. Código 90.20 de balances CMF/SP) contra bases de
proveedores del Estado (Mercado Público), declaraciones de intereses (InfoProbidad) o mallas societarias,
detectando coincidencias incluso cuando faltan segundos apellidos, tildes o existen variaciones ortográficas.

Uso:
  .venv/bin/python kit-journalism/scripts/cruce_difuso_entidades.py --auditar-afp
"""

import argparse
import json
from pathlib import Path

from rapidfuzz import fuzz, process
from normality import normalize


def normalizar_nombre(nombre: str) -> str:
    return normalize(nombre or "", latinize=True) or ""


def cruzar_listas_nombres(lista_a: list[dict], lista_b: list[dict], umbral: float = 86.0) -> list[dict]:
    """
    Cruza dos listas de diccionarios con clave 'nombre' usando Token Sort Ratio y WRatio de RapidFuzz (C++).
    """
    coincidencias = []
    mapa_b = {normalizar_nombre(item["nombre"]): item for item in lista_b if item.get("nombre")}
    claves_b = list(mapa_b.keys())

    for item_a in lista_a:
        nom_a = item_a.get("nombre", "")
        norm_a = normalizar_nombre(nom_a)
        if not norm_a or not claves_b:
            continue
        mejores = process.extract(
            norm_a,
            claves_b,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=umbral,
            limit=3,
        )
        for match_norm, score, _ in mejores:
            item_b = mapa_b[match_norm]
            coincidencias.append(
                {
                    "nombre_origen": nom_a,
                    "origen_meta": {k: v for k, v in item_a.items() if k != "nombre"},
                    "nombre_coincidente": item_b.get("nombre"),
                    "coincidente_meta": {k: v for k, v in item_b.items() if k != "nombre"},
                    "similitud_pct": round(score, 2),
                }
            )
    return coincidencias


def auditar_directores_afp(json_forense_path: Path) -> dict:
    data = json.loads(json_forense_path.read_text(encoding="utf-8"))
    ejecutivos = []
    for item in data.get("archivos_auditados", []):
        afp = item.get("archivo", "").replace("cmf_afp_", "").replace("_eeff_2024_12.pdf", "").upper()
        for p in item.get("administracion_9020", []):
            ejecutivos.append(
                {
                    "afp": afp,
                    "cargo": p.get("cargo", ""),
                    "nombre": p.get("nombre", ""),
                    "norm": normalizar_nombre(p.get("nombre", "")),
                }
            )

    repetidos = []
    for i, e1 in enumerate(ejecutivos):
        for e2 in ejecutivos[i + 1 :]:
            score = fuzz.token_sort_ratio(e1["norm"], e2["norm"])
            if score >= 85.0 and e1["afp"] != e2["afp"]:
                repetidos.append(
                    {
                        "persona_1": f"{e1['nombre']} ({e1['afp']} - {e1['cargo']})",
                        "persona_2": f"{e2['nombre']} ({e2['afp']} - {e2['cargo']})",
                        "similitud_pct": round(score, 2),
                    }
                )

    return {
        "total_ejecutivos_y_directores_indexados": len(ejecutivos),
        "cruces_inter_afp_detectados": repetidos,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Motor de resolución de entidades y cruce difuso de nombres (RapidFuzz + Normality)"
    )
    parser.add_argument(
        "--auditar-afp",
        action="store_true",
        help="Audita la nómina de directores y gerentes de las 7 AFP extraída en auditoria_forense_ifrs_sec.json",
    )
    args = parser.parse_args()

    if args.auditar_afp:
        path = Path("reportajes/Bonos Ejecutivos AFP/auditoria_forense_ifrs_sec.json")
        res = auditar_directores_afp(path)
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
