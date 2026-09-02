#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Última Prensa - Extractor y Formateador Pericial de InfoProbidad
====================================================================
Descarga, extrae y formatea al 100% las Declaraciones de Intereses
y Patrimonio (DIP) de autoridades públicas desde InfoProbidad.cl.

Soporta todos los formatos de URL y códigos:
- URLs directas: /Declaracion/Declaracion?ID=1698949
- URLs con hash: /Declaracion/BuscarDeclaracion?declaracion=cd68d24...
- IDs numéricos o hashes de 32 caracteres.

Uso:
    python scripts/extractor_infoprobidad.py "https://www.infoprobidad.cl/Declaracion/Declaracion?ID=1698949"
    python scripts/extractor_infoprobidad.py 1698949 --dest "alcalde llanquihue/documentos"
"""

import sys
import os
import re
import json
import argparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path


def descargar_declaracion_html(entrada: str) -> tuple[str, str]:
    """
    Descarga el HTML de la declaración soportando URLs completas o identificadores.
    Retorna (html_text, id_detectado).
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
    })

    # Si es una URL completa
    if entrada.startswith("http://") or entrada.startswith("https://"):
        try:
            resp = session.get(entrada, timeout=25)
            if resp.status_code == 200 and "Declaración no disponible" not in resp.text and len(resp.text) > 10000:
                # Extraer ID de la URL
                match_id = re.search(r'(?:ID=|declaracion=|IDCargo=)([a-zA-Z0-9]+)', entrada)
                id_detectado = match_id.group(1) if match_id else "web"
                return resp.text, id_detectado
        except Exception as e:
            print(f"[!] Error al descargar URL directa: {e}")

    # Si es un ID o hash
    identificador = entrada.strip()
    match_hash = re.search(r'([a-fA-F0-9]{32})', identificador)
    match_num = re.search(r'(\d+)', identificador)

    urls_a_probar = []
    if match_hash:
        h = match_hash.group(1)
        urls_a_probar.extend([
            f"https://www.infoprobidad.cl/Declaracion/BuscarDeclaracion?declaracion={h}",
            f"https://www.infoprobidad.cl/Declaracion/BuscarDeclaracion?IDCargo={h}",
        ])
    if match_num:
        n = match_num.group(1)
        urls_a_probar.extend([
            f"https://www.infoprobidad.cl/Declaracion/Declaracion?ID={n}",
            f"https://www.infoprobidad.cl/Declaracion/BuscarDeclaracion?ID={n}",
        ])

    for u in urls_a_probar:
        try:
            resp = session.get(u, timeout=25)
            if resp.status_code == 200 and "Declaración no disponible" not in resp.text and len(resp.text) > 10000:
                return resp.text, identificador
        except Exception as e:
            pass

    # Último intento directo
    resp = session.get(entrada if entrada.startswith("http") else f"https://www.infoprobidad.cl/Declaracion/Declaracion?ID={identificador}", timeout=25)
    return resp.text, identificador


def parsear_declaracion(html: str) -> dict:
    """Parsea exhaustivamente todas las tablas y secciones de la declaración."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Nombre del Declarante
    h1 = soup.find('h1')
    nombre_declarante = h1.get_text(strip=True) if h1 else "Declarante Desconocido"
    
    # 2. Recorrer todas las tablas
    tables = soup.find_all('table')
    
    datos = {
        "nombre_declarante": nombre_declarante,
        "datos_declaracion": {},
        "datos_personales": {},
        "conyuge_o_conviviente": {},
        "parientes": [],
        "cargos_ejercicio": [],
        "actividades_profesionales": [],
        "bienes_inmuebles": [],
        "vehiculos": [],
        "sociedades_empresas": [],
        "valores_instrumentos": [],
        "pasivos_deudas": [],
        "otras_fuentes_interes": []
    }
    
    for t in tables:
        rows = t.find_all('tr')
        if not rows:
            continue
            
        dict_filas = {}
        for r in rows:
            th = r.find('th')
            td = r.find('td')
            if th and td:
                k = th.get_text(strip=True)
                v = td.get_text(strip=True)
                dict_filas[k] = v
            else:
                cells = [c.get_text(strip=True) for c in r.find_all(['td', 'th'])]
                if len(cells) == 2:
                    dict_filas[cells[0]] = cells[1]
        
        llaves_texto = " ".join(dict_filas.keys()).lower()
        valores_texto = " ".join(dict_filas.values()).lower()
        
        if "renta bruta" in llaves_texto or "organismo" in llaves_texto:
            datos["datos_declaracion"].update(dict_filas)
        elif "apellido paterno" in llaves_texto and "profesión" in llaves_texto:
            datos["datos_personales"].update(dict_filas)
        elif "apellido paterno" in llaves_texto and "nombres" in llaves_texto and "profesión" not in llaves_texto:
            datos["conyuge_o_conviviente"].update(dict_filas)
        elif "parentesco" in llaves_texto:
            datos["parientes"].append(dict_filas)
        elif "fecha de asunción" in llaves_texto or "servicio/entidad" in llaves_texto:
            datos["cargos_ejercicio"].append(dict_filas)
        elif "fojas" in llaves_texto or "n° de inscripción" in llaves_texto or "comuna" in llaves_texto:
            datos["bienes_inmuebles"].append(dict_filas)
        elif "tipo de vehículo" in llaves_texto or "marca" in llaves_texto or "modelo" in llaves_texto:
            datos["vehiculos"].append(dict_filas)
        elif "r.u.t." in llaves_texto or ("razón social" in llaves_texto and "acreedor" not in llaves_texto):
            if "título (derecho o acción)" in llaves_texto or "giro registrado" in llaves_texto:
                datos["sociedades_empresas"].append(dict_filas)
            elif "apv" in valores_texto or "fondos mutuos" in valores_texto or "emisor" in llaves_texto:
                datos["valores_instrumentos"].append(dict_filas)
        elif "monto adeudado" in llaves_texto or "tipo de obligación" in llaves_texto or "acreedor" in llaves_texto:
            datos["pasivos_deudas"].append(dict_filas)
        elif "tipo de actividad" in llaves_texto:
            datos["actividades_profesionales"].append(dict_filas)
            
    return datos


def generar_markdown(datos: dict, declaracion_id: str, url_fuente: str) -> str:
    """Genera un informe completo en formato Markdown."""
    lines = []
    lines.append(f"# Declaración de Intereses y Patrimonio (DIP) - {datos['nombre_declarante']}")
    lines.append(f"\n**Identificador:** `{declaracion_id}`  ")
    lines.append(f"**Fuente Oficial:** [{url_fuente}]({url_fuente})  \n")
    lines.append("---")
    
    # 1. Datos de la Declaración
    lines.append("\n## 1. Datos de la Declaración y Cargo Público")
    for k, v in datos["datos_declaracion"].items():
        lines.append(f"- **{k}:** {v}")
    for k, v in datos["datos_personales"].items():
        lines.append(f"- **{k}:** {v}")
        
    # 2. Cónyuge y Parentesco
    if datos["conyuge_o_conviviente"]:
        lines.append("\n## 2. Cónyuge o Conviviente Civil")
        for k, v in datos["conyuge_o_conviviente"].items():
            lines.append(f"- **{k}:** {v}")
            
    if datos["parientes"]:
        lines.append("\n## 3. Red Familiar y Parientes Declarados")
        for p in datos["parientes"]:
            nom = p.get("Nombre", p.get("Nombres", "No especificado"))
            par = p.get("Parentesco", "Parentesco reservado")
            lines.append(f"- **{par}:** {nom}")
            
    # 4. Bienes Inmuebles
    lines.append("\n## 4. Bienes Inmuebles y Propiedades")
    if datos["bienes_inmuebles"]:
        for i, b in enumerate(datos["bienes_inmuebles"], 1):
            lines.append(f"\n### Inmueble #{i}")
            for k, v in b.items():
                lines.append(f"- **{k}:** {v}")
    else:
        lines.append("*No registra bienes inmuebles declarados.*")
        
    # 5. Vehículos
    lines.append("\n## 5. Vehículos Motorizados")
    if datos["vehiculos"]:
        for i, vh in enumerate(datos["vehiculos"], 1):
            lines.append(f"\n### Vehículo #{i}")
            for k, v in vh.items():
                lines.append(f"- **{k}:** {v}")
    else:
        lines.append("*No registra vehículos declarados.*")
        
    # 6. Sociedades y Empresas
    lines.append("\n## 6. Comunidades, Sociedades y Empresas")
    if datos["sociedades_empresas"]:
        for i, soc in enumerate(datos["sociedades_empresas"], 1):
            lines.append(f"\n### Sociedad #{i}")
            for k, v in soc.items():
                lines.append(f"- **{k}:** {v}")
    else:
        lines.append("*No registra participación en sociedades.*")
        
    # 7. Valores e Instrumentos
    lines.append("\n## 7. Valores, Fondos Mutuos y APV")
    if datos["valores_instrumentos"]:
        for i, val in enumerate(datos["valores_instrumentos"], 1):
            lines.append(f"\n### Instrumento #{i}")
            for k, v in val.items():
                lines.append(f"- **{k}:** {v}")
    else:
        lines.append("*No registra valores o instrumentos transables.*")
        
    # 8. Pasivos y Deudas
    lines.append("\n## 8. Pasivos y Deudas")
    if datos["pasivos_deudas"]:
        for i, pas in enumerate(datos["pasivos_deudas"], 1):
            lines.append(f"\n### Deuda #{i}")
            for k, v in pas.items():
                lines.append(f"- **{k}:** {v}")
    else:
        lines.append("*No registra pasivos ni deudas declaradas.*")
        
    return "\n".join(lines)


def generar_html_imprimible(datos: dict, declaracion_id: str, url_fuente: str) -> str:
    """Genera un archivo HTML con diseño editorial impecable, listo para imprimir en PDF."""
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>DIP - {datos['nombre_declarante']}</title>
    <style>
        @page {{
            size: A4;
            margin: 15mm 15mm 20mm 15mm;
            @bottom-right {{
                content: counter(page) " de " counter(pages);
            }}
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #1e293b;
            line-height: 1.5;
            background-color: #f8fafc;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        }}
        .header {{
            border-bottom: 3px solid #0284c7;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .badge {{
            display: inline-block;
            background: #e0f2fe;
            color: #0369a1;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }}
        h1 {{
            margin: 8px 0;
            color: #0f172a;
            font-size: 26px;
        }}
        .meta-info {{
            color: #64748b;
            font-size: 13px;
        }}
        .section-title {{
            background: #f1f5f9;
            color: #0f172a;
            font-size: 16px;
            font-weight: 700;
            padding: 10px 14px;
            border-radius: 6px;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #0284c7;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 13px;
        }}
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background: #f8fafc;
            color: #475569;
            font-weight: 600;
            width: 35%;
        }}
        td {{
            color: #1e293b;
        }}
        .data-card {{
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 15px;
            background: #ffffff;
            margin-bottom: 15px;
        }}
        .card-header {{
            font-weight: bold;
            color: #0369a1;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 40px;
            border-top: 1px solid #e2e8f0;
            padding-top: 15px;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
        }}
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 0;
                max-width: 100%;
            }}
            .section-title {{
                break-after: avoid;
            }}
            .data-card, table {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">InfoProbidad • Dossier Pericial</span>
            <h1>{datos['nombre_declarante']}</h1>
            <div class="meta-info">
                <strong>ID Declaración:</strong> <code>{declaracion_id}</code> | 
                <strong>Fuente Oficial:</strong> <a href="{url_fuente}" target="_blank">infoprobidad.cl</a>
            </div>
        </div>

        <div class="section-title">1. Datos de la Declaración y Cargo</div>
        <table>"""

    for k, v in {**datos["datos_declaracion"], **datos["datos_personales"]}.items():
        html_template += f"<tr><th>{k}</th><td>{v}</td></tr>\n"

    html_template += "</table>"

    # Cónyuge y Parientes
    if datos["conyuge_o_conviviente"] or datos["parientes"]:
        html_template += '<div class="section-title">2. Cónyuge y Red Familiar</div>'
        if datos["conyuge_o_conviviente"]:
            html_template += "<table>"
            for k, v in datos["conyuge_o_conviviente"].items():
                html_template += f"<tr><th>Cónyuge ({k})</th><td>{v}</td></tr>\n"
            html_template += "</table>"
            
        if datos["parientes"]:
            html_template += "<table><tr><th>Parentesco</th><th>Nombre Declarado</th></tr>"
            for p in datos["parientes"]:
                nom = p.get("Nombre", p.get("Nombres", "No especificado"))
                par = p.get("Parentesco", "Parentesco reservado")
                html_template += f"<tr><td><strong>{par}</strong></td><td>{nom}</td></tr>\n"
            html_template += "</table>"

    # Bienes Inmuebles
    html_template += '<div class="section-title">3. Bienes Inmuebles</div>'
    if datos["bienes_inmuebles"]:
        for i, b in enumerate(datos["bienes_inmuebles"], 1):
            html_template += f'<div class="data-card"><div class="card-header">Inmueble #{i} - {b.get("Comuna", "")} ({b.get("Dirección", "")})</div><table>'
            for k, v in b.items():
                html_template += f"<tr><th>{k}</th><td>{v}</td></tr>\n"
            html_template += "</table></div>"
    else:
        html_template += "<p style='font-size:13px; color:#64748b; font-style:italic;'>No registra bienes inmuebles declarados.</p>"

    # Vehículos
    html_template += '<div class="section-title">4. Vehículos Motorizados</div>'
    if datos["vehiculos"]:
        for i, vh in enumerate(datos["vehiculos"], 1):
            html_template += f'<div class="data-card"><div class="card-header">Vehículo #{i} - {vh.get("Marca", "")} {vh.get("Modelo", "")} ({vh.get("Año de fabricación", "")})</div><table>'
            for k, v in vh.items():
                html_template += f"<tr><th>{k}</th><td>{v}</td></tr>\n"
            html_template += "</table></div>"
    else:
        html_template += "<p style='font-size:13px; color:#64748b; font-style:italic;'>No registra vehículos declarados.</p>"

    # Sociedades y Empresas
    html_template += '<div class="section-title">5. Comunidades, Sociedades y Empresas</div>'
    if datos["sociedades_empresas"]:
        for i, soc in enumerate(datos["sociedades_empresas"], 1):
            html_template += f'<div class="data-card"><div class="card-header">Sociedad #{i} - {soc.get("Nombre o Razón Social", "")} (RUT: {soc.get("R.U.T.", "")})</div><table>'
            for k, v in soc.items():
                html_template += f"<tr><th>{k}</th><td>{v}</td></tr>\n"
            html_template += "</table></div>"
    else:
        html_template += "<p style='font-size:13px; color:#64748b; font-style:italic;'>No registra sociedades declaradas.</p>"

    # Valores e Instrumentos
    if datos["valores_instrumentos"]:
        html_template += '<div class="section-title">6. Valores, Fondos Mutuos y APV</div>'
        for i, val in enumerate(datos["valores_instrumentos"], 1):
            html_template += f'<div class="data-card"><div class="card-header">Instrumento #{i} - {val.get("Título o documento", "")} ({val.get("Nombre o Razón Social del emisor", "")})</div><table>'
            for k, v in val.items():
                html_template += f"<tr><th>{k}</th><td>{v}</td></tr>\n"
            html_template += "</table></div>"

    # Pasivos y Deudas
    html_template += '<div class="section-title">7. Pasivos y Obligaciones Financieras (Deudas)</div>'
    if datos["pasivos_deudas"]:
        for i, pas in enumerate(datos["pasivos_deudas"], 1):
            html_template += f'<div class="data-card"><div class="card-header">Deuda #{i} - {pas.get("Tipo de obligación o deuda", "")} con {pas.get("Nombre o Razón Social del acreedor", "")} ({pas.get("Monto adeudado en pesos", "")})</div><table>'
            for k, v in pas.items():
                html_template += f"<tr><th>{k}</th><td>{v}</td></tr>\n"
            html_template += "</table></div>"
    else:
        html_template += "<p style='font-size:13px; color:#64748b; font-style:italic;'>No registra pasivos declarados.</p>"

    html_template += f"""
        <div class="footer">
            Procesado con <strong>Última Prensa IA Journalism Kit</strong> • Ley N° 20.880 sobre Probidad en la Función Pública
        </div>
    </div>
</body>
</html>"""
    return html_template


def main():
    parser = argparse.ArgumentParser(description="Extractor de declaraciones completas de InfoProbidad.")
    parser.add_argument("url_o_id", help="URL completa de InfoProbidad, hash de 32 caracteres o ID numérico")
    parser.add_argument("--dest", default="", help="Carpeta de destino donde guardar el archivo (ej. 'alcalde llanquihue/documentos')")
    parser.add_argument("--prefix", default="DIP", help="Prefijo para los nombres de archivo (por defecto 'DIP')")
    args = parser.parse_args()

    url_entrada = args.url_o_id.strip()
    print(f"[+] Conectando a InfoProbidad: {url_entrada}")
    
    html, declaracion_id = descargar_declaracion_html(url_entrada)
    if "Declaración no disponible" in html or len(html) < 5000:
        print("[-] Error: La declaración no está disponible o el ID es inválido.")
        sys.exit(1)
        
    datos = parsear_declaracion(html)
    nombre = datos['nombre_declarante']
    print(f"[+] Declarante detectado: {nombre}")
    
    # Construir nombre limpio para archivos: DIP_[Nombre_Persona]_[Fecha]
    nombre_limpio = re.sub(r'[^a-zA-Z0-9_]', '_', nombre.strip())
    # Normalizar espacios duplicados
    nombre_limpio = re.sub(r'_+', '_', nombre_limpio).strip('_')
    
    fecha_decl = datos["datos_declaracion"].get("Fecha", "").replace("-", "")
    base_filename = f"{args.prefix}_{nombre_limpio}"
    if fecha_decl:
        base_filename += f"_{fecha_decl}"
        
    url_fuente = url_entrada if url_entrada.startswith("http") else f"https://www.infoprobidad.cl/Declaracion/Declaracion?ID={declaracion_id}"
    
    # Directorio de destino
    dest_dir = Path(args.dest) if args.dest else Path("reportajes/declaraciones_patrimonio") / base_filename
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Guardar Markdown
    md_file = dest_dir / f"{base_filename}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(generar_markdown(datos, declaracion_id, url_fuente))
    print(f"[+] Markdown generado: {md_file.resolve()}")
    
    # 2. Guardar HTML Imprimible
    html_file = dest_dir / f"{base_filename}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(generar_html_imprimible(datos, declaracion_id, url_fuente))
    print(f"[+] HTML Imprimible generado: {html_file.resolve()}")
    
    # 3. Guardar JSON
    json_file = dest_dir / f"{base_filename}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"[+] JSON estructurado generado: {json_file.resolve()}")
    
    print(f"\n[OK] DIP guardada exitosamente como '{base_filename}' en '{dest_dir}'.")


if __name__ == "__main__":
    main()
