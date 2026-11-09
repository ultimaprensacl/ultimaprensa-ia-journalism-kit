#!/usr/bin/env python3
"""
cruce_probabilistico_splink.py — Deduplicación y cruce masivo de registros públicos con Splink 5 + DuckDB
Permite cruzar nóminas de autoridades/ejecutivos (CMF, InfoProbidad, Lobby) contra proveedores
de Mercado Público o mallas societarias usando el modelo probabilístico Fellegi-Sunter sobre DuckDB.

Uso:
  .venv/bin/python kit-journalism/scripts/cruce_probabilistico_splink.py --demo
"""

import argparse
import json
import pandas as pd
import splink.comparison_library as cl
from splink import DuckDBAPI, Linker, SettingsCreator, block_on


def ejecutar_cruce_splink(df_registros: pd.DataFrame) -> list[dict]:
    settings = SettingsCreator(
        link_type="dedupe_only",
        blocking_rules_to_generate_predictions=[
            block_on("primer_apellido"),
            block_on("primer_nombre"),
        ],
        comparisons=[
            cl.NameComparison("primer_nombre"),
            cl.NameComparison("primer_apellido"),
            cl.ExactMatch("entidad").configure(term_frequency_adjustments=True),
        ],
        retain_intermediate_calculation_columns=False,
    )

    db_api = DuckDBAPI()
    splink_df = db_api.register(df_registros)
    linker = Linker(splink_df, settings)
    linker.training.estimate_u_using_random_sampling(max_pairs=1e5)

    preds = linker.inference.predict(threshold_match_probability=0.75)
    df_preds = preds.as_pandas_dataframe()
    resultados = []
    for _, row in df_preds.iterrows():
        resultados.append(
            {
                "id_1": str(row.get("unique_id_l")),
                "id_2": str(row.get("unique_id_r")),
                "nombre_1": f"{row.get('primer_nombre_l', '')} {row.get('primer_apellido_l', '')}",
                "nombre_2": f"{row.get('primer_nombre_r', '')} {row.get('primer_apellido_r', '')}",
                "entidad_1": str(row.get("entidad_l", "")),
                "entidad_2": str(row.get("entidad_r", "")),
                "probabilidad_match": round(float(row.get("match_probability", 0.0)), 4),
            }
        )
    return resultados


def main():
    parser = argparse.ArgumentParser(
        description="Cruce probabilístico de registros públicos con Splink 5 + DuckDB"
    )
    parser.add_argument("--demo", action="store_true", help="Ejecuta prueba de verificación de Splink + DuckDB")
    args = parser.parse_args()

    if args.demo:
        datos = [
            {"unique_id": 1, "primer_nombre": "Santiago", "primer_apellido": "Donoso", "entidad": "AFP Provida"},
            {"unique_id": 2, "primer_nombre": "Santiago", "primer_apellido": "Donoso Hue", "entidad": "MetLife Chile"},
            {"unique_id": 3, "primer_nombre": "Alejandro", "primer_apellido": "Bezanilla", "entidad": "AFP Habitat"},
            {"unique_id": 4, "primer_nombre": "Alejandro", "primer_apellido": "Bezanilla Mena", "entidad": "Inversiones La Construccion"},
            {"unique_id": 5, "primer_nombre": "Renzo", "primer_apellido": "Vercelli", "entidad": "AFP Capital"},
        ]
        df = pd.DataFrame(datos)
        matches = ejecutar_cruce_splink(df)
        print(json.dumps({"estado": "splink_5_duckdb_operativo", "coincidencias_detectadas": matches}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
