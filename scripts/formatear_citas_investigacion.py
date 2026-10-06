#!/usr/bin/env python3
"""
formatear_citas_investigacion.py – Validador y generador de citas documentales
según normas APA 7ma Edición (Legal References) y estándares GIJN/IRE
para la Unidad de Investigación de Última Prensa.
"""

import sys
import json
import argparse
from typing import Dict, Any, List

TIPOS_FUENTE = {
    "resolucion": "Resoluciones y Actos Administrativos",
    "judicial": "Causas Judiciales y Sentencias",
    "participacion_ciudadana": "Observaciones Ciudadanas y Expedientes PAC",
    "peritaje": "Informes Técnicos y Peritajes Geomecánicos",
    "normativa": "Tratados Internacionales y Normativa Legal",
    "satelital": "Teledetección Satelital y Registros Cartográficos"
}

def formatear_cita(item: Dict[str, Any]) -> str:
    tipo = item.get("tipo", "general")
    if tipo == "resolucion":
        emisor = item.get("emisor", "")
        fecha = item.get("fecha", "")
        titulo = item.get("titulo", "")
        numero = item.get("numero", "")
        expediente = item.get("expediente", "")
        url = item.get("url", "")
        ref = f"{emisor}. ({fecha}). *{titulo}* ({numero}). {expediente}."
        if url:
            ref += f" {url}"
        return ref

    elif tipo == "judicial":
        tribunal = item.get("tribunal", "")
        fecha = item.get("fecha", "")
        caratula = item.get("caratula", "")
        rol = item.get("rol", "")
        detalle = item.get("detalle", "")
        return f"{tribunal}. ({fecha}). *{caratula}* ({rol}). {detalle}."

    elif tipo == "participacion_ciudadana":
        autor = item.get("autor", "")
        fecha = item.get("fecha", "")
        titulo = item.get("titulo", "")
        folio = item.get("folio", "")
        organismo = item.get("organismo", "")
        return f"{autor}. ({fecha}). *{titulo}* ({folio}). {organismo}."

    elif tipo == "peritaje":
        autor = item.get("autor", "")
        fecha = item.get("fecha", "")
        titulo = item.get("titulo", "")
        mandante = item.get("mandante", "")
        return f"{autor}. ({fecha}). *{titulo}*. {mandante}."

    elif tipo == "normativa":
        emisor = item.get("emisor", "")
        fecha = item.get("fecha", "")
        nombre = item.get("nombre", "")
        publicacion = item.get("publicacion", "")
        return f"{emisor}. ({fecha}). *{nombre}*. {publicacion}."

    elif tipo == "satelital":
        proveedor = item.get("proveedor", "")
        fecha = item.get("fecha", "")
        descripcion = item.get("descripcion", "")
        coordenadas = item.get("coordenadas", "")
        return f"{proveedor}. ({fecha}). *{descripcion}* [{coordenadas}]."

    else:
        autor = item.get("autor", "Fuente oficial")
        fecha = item.get("fecha", "s.f.")
        titulo = item.get("titulo", "")
        detalle = item.get("detalle", "")
        return f"{autor}. ({fecha}). *{titulo}*. {detalle}."

def generar_seccion_markdown(fuentes: List[Dict[str, Any]]) -> str:
    lineas = ["## Fuentes y referencias documentales", ""]
    lineas.append("*Compiladas bajo los estándares APA 7ma Edición (referencias legales y administrativas) y las normas de verificación de la Red Global de Periodismo de Investigación (GIJN).*")
    lineas.append("")

    agrupadas: Dict[str, List[Dict[str, Any]]] = {}
    for f in fuentes:
        t = f.get("tipo", "otros")
        agrupadas.setdefault(t, []).append(f)

    for tipo, titulo_seccion in TIPOS_FUENTE.items():
        if tipo in agrupadas:
            lineas.append(f"### {titulo_seccion}")
            for item in agrupadas[tipo]:
                lineas.append(f"- {formatear_cita(item)}")
            lineas.append("")

    return "\n".join(lineas)

def main():
    parser = argparse.ArgumentParser(description="Generador de citas documentales APA 7 / GIJN")
    parser.add_argument("--json", help="Archivo JSON con listado de fuentes")
    parser.add_argument("--out", help="Archivo de salida markdown")
    args = parser.parse_args()

    if args.json:
        with open(args.json, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        md = generar_seccion_markdown(data)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fp:
                fp.write(md)
            print(f"[+] Fuentes exportadas a {args.out}")
        else:
            print(md)
    else:
        print("[*] Script de citación periodística cargado. Use --help para ver opciones.")

if __name__ == "__main__":
    main()
