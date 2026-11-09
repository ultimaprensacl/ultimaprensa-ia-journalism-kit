#!/usr/bin/env python3
"""
auditoria_geoespacial_raster.py — Peritaje satelital y territorial (Rasterio + GeoPandas + PyProj)
Permite auditar polígonos de concesiones mineras, acuícolas, humedales urbanos, loteos irregulares
o bienes nacionales de uso público (BNUP), calculando superficies exactas en hectáreas (UTM Huso 18S / 19S,
SIRGAS-Chile EPSG:5361 / EPSG:32719) y extrayendo metadatos o bandas de imágenes satelitales GeoTIFF.

Uso:
  .venv/bin/python kit-journalism/scripts/auditoria_geoespacial_raster.py --verificar
"""

import argparse
import json
from pathlib import Path

import geopandas as gpd
import pyproj
import rasterio
from shapely.geometry import Polygon


def calcular_superficie_poligono_ha(coords_lon_lat: list[tuple[float, float]], epsg_utm: int = 32719) -> dict:
    poly = Polygon(coords_lon_lat)
    gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[poly], crs="EPSG:4326")
    gdf_utm = gdf.to_crs(epsg=epsg_utm)
    area_m2 = float(gdf_utm.geometry.area.iloc[0])
    perimetro_m = float(gdf_utm.geometry.length.iloc[0])
    return {
        "crs_proyeccion": f"EPSG:{epsg_utm}",
        "superficie_m2": round(area_m2, 2),
        "superficie_hectareas": round(area_m2 / 10000.0, 4),
        "perimetro_metros": round(perimetro_m, 2),
    }


def inspeccionar_geotiff(tiff_path: Path) -> dict:
    with rasterio.open(tiff_path) as src:
        return {
            "archivo": str(tiff_path),
            "crs": str(src.crs),
            "dimensiones_px": [src.width, src.height],
            "bandas": src.count,
            "limites_geograficos": list(src.bounds),
            "resolucion_espacial": list(src.res),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Peritaje geoespacial y satelital con Rasterio, GeoPandas y PyProj"
    )
    parser.add_argument("--verificar", action="store_true", help="Verifica el motor geoespacial UTM 19S")
    parser.add_argument("--geotiff", default="", help="Ruta a imagen satelital GeoTIFF para auditar")
    args = parser.parse_args()

    if args.geotiff:
        res = inspeccionar_geotiff(Path(args.geotiff))
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.verificar:
        # Polígono de prueba en coordenadas WGS84 proyectado a UTM 19S (EPSG:32719)
        coords = [
            (-70.6500, -33.4400),
            (-70.6480, -33.4400),
            (-70.6480, -33.4420),
            (-70.6500, -33.4420),
        ]
        res = calcular_superficie_poligono_ha(coords, epsg_utm=32719)
        res["versiones"] = {
            "geopandas": gpd.__version__,
            "rasterio": rasterio.__version__,
            "pyproj": pyproj.__version__,
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
