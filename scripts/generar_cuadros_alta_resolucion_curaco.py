#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_cuadros_alta_resolucion_curaco.py
Genera infografías y tablas de alta resolución (2x Retina) para el reportaje de Curaco,
las renderiza con Headless Chrome y las sube automáticamente al CDN de Substack.
"""

import os
import sys
import json
import base64
import subprocess
import urllib.request
from pathlib import Path

CHROME_BIN = "/home/pablo/.cache/puppeteer/chrome/linux-153.0.8010.36/chrome-linux64/chrome"
if not os.path.exists(CHROME_BIN):
    CHROME_BIN = "/home/pablo/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"

SUBSTACK_SID = os.environ.get("SUBSTACK_SID", "s:UpGj0faXPPR4zmpR_8ICzH_mQTzPXYl3.j5kwnYjtkxIiPWjoTmLISTszDXKGZ8dDEETIP+32zxc")
PUBLICATION = os.environ.get("SUBSTACK_SUBDOMAIN", "ultimaprensacl")

CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: #f1f5f9;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 24px;
    -webkit-font-smoothing: antialiased;
}

.card {
    width: 820px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
    overflow: hidden;
}

.card-header {
    background: #0f172a;
    padding: 20px 28px;
    color: #ffffff;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #d9381e;
}

.card-title-group h2 {
    font-size: 17px;
    font-weight: 800;
    letter-spacing: -0.3px;
    color: #ffffff;
    margin-bottom: 4px;
    text-transform: uppercase;
}

.card-title-group p {
    font-size: 13px;
    color: #94a3b8;
}

.badge {
    background: #d9381e;
    color: #ffffff;
    font-size: 10.5px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 5px 10px;
    border-radius: 6px;
}

.card-body {
    padding: 24px 28px;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
    line-height: 1.5;
}

th {
    background: #f8fafc;
    color: #334155;
    font-weight: 700;
    text-align: left;
    padding: 10px 14px;
    border-bottom: 2px solid #e2e8f0;
    font-size: 12.5px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

td {
    padding: 11px 14px;
    border-bottom: 1px solid #f1f5f9;
    color: #334155;
    vertical-align: top;
}

tr:nth-child(even) {
    background: #fcfcfd;
}

.date-col {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    color: #0f172a;
    white-space: nowrap;
    width: 115px;
}

.date-alert {
    color: #b91c1c;
    background: #fef2f2;
}

.alert-row {
    background: #fff1f2 !important;
}

.alert-row td {
    color: #991b1b;
}

.final-row {
    background: #f8fafc !important;
    border-top: 2px solid #e2e8f0;
    font-weight: 600;
}

.card-footer {
    background: #f8fafc;
    padding: 12px 28px;
    border-top: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11.5px;
    color: #64748b;
}

.source-tag {
    font-weight: 600;
}
"""

HTML_CUADRO_1 = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>""" + CSS_BASE + """</style>
</head>
<body>
<div class="card">
    <div class="card-header">
        <div class="card-title-group">
            <h2>Cronología Forense: Las Fechas de la Maniobra Administrativa</h2>
            <p>Evolución documental del Relleno Curaco y la consumación de la caducidad legal</p>
        </div>
        <div class="badge">Última Prensa Forense</div>
    </div>
    <div class="card-body">
        <table>
            <thead>
                <tr>
                    <th style="width: 120px;">Fecha</th>
                    <th>Documento Oficial y Hecho Acreditado</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="date-col">22/01/2010</td>
                    <td><strong>RCA N° 43/2010:</strong> COREMA Los Lagos aprueba el Relleno Provincial con base en estudios de 2006-2008.</td>
                </tr>
                <tr>
                    <td class="date-col">24/10/2014</td>
                    <td><strong>ORD. N° 000425 (SEREMI):</strong> Advierte formalmente al Municipio que la RCA caduca el 26/01/2015.</td>
                </tr>
                <tr>
                    <td class="date-col">14/10/2014</td>
                    <td><strong>Firma de Contrato:</strong> Municipio y Servitrans pactan obras a contrarreloj para intentar frenar la caducidad.</td>
                </tr>
                <tr class="alert-row">
                    <td class="date-col date-alert">12/11/2014</td>
                    <td><strong>Colapso Geomecánico:</strong> Se desliza la ladera oeste sobre arcillas alofánicas trumao licuables.</td>
                </tr>
                <tr>
                    <td class="date-col">21/01/2015</td>
                    <td><strong>ORD. N° 070 (Alcaldía):</strong> Alcalde Jaime Bertín envía decretos al SEA para acreditar inicio, ocultando el derrumbe.</td>
                </tr>
                <tr class="alert-row">
                    <td class="date-col date-alert">13/10/2015</td>
                    <td><strong>Paralización Total:</strong> Municipio dicta <strong>Decreto N° 9.393</strong> suspendiendo todas las faenas por suelo no apto.</td>
                </tr>
                <tr>
                    <td class="date-col">22/12/2015</td>
                    <td><strong>Resolución Exenta N° 1697 (SEA):</strong> Da por iniciado el proyecto ¡dos meses después de su paralización decretada!</td>
                </tr>
                <tr>
                    <td class="date-col">10/06/2020</td>
                    <td><strong>Sentencia Civil (Rol C-351-2019):</strong> Resuelve contrato por culpa y negligencia exclusiva de la Municipalidad.</td>
                </tr>
                <tr>
                    <td class="date-col">30/05/2022</td>
                    <td><strong>Corte Suprema (Rol 69.455-2021):</strong> Homologa transacción de $3.177 millones y extingue judicialmente el contrato.</td>
                </tr>
                <tr class="final-row">
                    <td class="date-col" style="color: #b91c1c;">Sept. 2026</td>
                    <td><strong>Caducidad de Pleno Derecho:</strong> Se cumplen <strong>10 años y 9 meses</strong> de abandono continuo desde la resolución del SEA.</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="card-footer">
        <span class="source-tag">Fuente: Expediente SEIA N° 3675668 • PJUD Roles C-351-2019 y 69.455-2021</span>
        <span>© 2026 Última Prensa</span>
    </div>
</div>
</body>
</html>
"""

HTML_CUADRO_2 = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>""" + CSS_BASE + """
.actor-col {
    font-weight: 700;
    color: #0f172a;
    width: 260px;
}
.actor-sub {
    font-size: 11.5px;
    font-weight: 500;
    color: #64748b;
    margin-top: 2px;
}
.role-col {
    color: #334155;
    font-size: 13.5px;
}
</style>
</head>
<body>
<div class="card">
    <div class="card-header">
        <div class="card-title-group">
            <h2>El Entramado Institucional de la Reactivación 2026</h2>
            <p>Estructura de gobernanza y roles en la operación de USD $31 millones</p>
        </div>
        <div class="badge">Red de Poder</div>
    </div>
    <div class="card-body">
        <table>
            <thead>
                <tr>
                    <th>Entidad / Actor Clave</th>
                    <th>Rol Estratégico en la Operación</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="actor-col">
                        Subdere y BID
                        <div class="actor-sub">Gobierno Central & Organismo Multilateral</div>
                    </td>
                    <td class="role-col">
                        Diseñan el paquete de financiamiento proyectado en <strong>USD $31 millones</strong> para reactivar obras eludiendo un nuevo EIA.
                    </td>
                </tr>
                <tr>
                    <td class="actor-col">
                        Delegación Presidencial Provincial
                        <div class="actor-sub">Alejandro Rehbein Caerols</div>
                    </td>
                    <td class="role-col">
                        Asume la vocería política del Ejecutivo para presionar por el inicio de faenas civiles pesadas durante el segundo semestre de 2026.
                    </td>
                </tr>
                <tr>
                    <td class="actor-col">
                        Gobierno Regional de Los Lagos
                        <div class="actor-sub">Gobernador Alejandro Santana</div>
                    </td>
                    <td class="role-col">
                        Valida técnicamente el terreno tras drenar 200 000 m³ de agua de lluvia y napas, descartando públicamente buscar un nuevo predio.
                    </td>
                </tr>
                <tr>
                    <td class="actor-col">
                        Asociación de Municipios de Osorno
                        <div class="actor-sub">Alcaldes de las 7 comunas provinciales</div>
                    </td>
                    <td class="role-col">
                        Instalan la narrativa de «urgencia sanitaria provincial» por el colapso del vertedero histórico para blindar el plan de reactivación.
                    </td>
                </tr>
                <tr class="final-row">
                    <td class="actor-col">
                        Municipalidad de Osorno (SECPLAN)
                        <div class="actor-sub">Alcalde Jaime Bertín / Unidad Técnica</div>
                    </td>
                    <td class="role-col">
                        Unidad ejecutora: publica licitaciones en Mercado Público (ID <code>2308-119-LR25</code>) para drenar la fosa y contratar obras complementarias.
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="card-footer">
        <span class="source-tag">Fuente: Mercado Público • Decretos GORE Los Lagos • Declaraciones Oficiales 2026</span>
        <span>© 2026 Última Prensa</span>
    </div>
</div>
</body>
</html>
"""

HTML_CUADRO_3 = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>""" + CSS_BASE + """
.grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 16px;
    margin-top: 4px;
}
.grid-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 18px;
    display: flex;
    flex-direction: column;
}
.box-num {
    font-size: 11px;
    font-weight: 800;
    color: #d9381e;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}
.box-title {
    font-size: 14.5px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.3;
    margin-bottom: 10px;
}
.box-desc {
    font-size: 12.5px;
    line-height: 1.6;
    color: #475569;
    flex-grow: 1;
}
.box-highlight {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 10px;
    margin-top: 10px;
    font-size: 11.5px;
    font-weight: 600;
    color: #0f172a;
}
</style>
</head>
<body>
<div class="card" style="width: 820px;">
    <div class="card-header">
        <div class="card-title-group">
            <h2>Ejes Estratégicos: El Flanco Internacional y la Ofensiva Jurídica</h2>
            <p>Los tres factores críticos que condicionan el futuro de Curaco en 2026</p>
        </div>
        <div class="badge">Estrategia Legal</div>
    </div>
    <div class="card-body">
        <div class="grid-container">
            <div class="grid-box">
                <div class="box-num">Eje 1 • Multilateral</div>
                <div class="box-title">Activación del MICI ante el BID</div>
                <div class="box-desc">
                    El Marco ESPS del BID prohíbe financiar proyectos con permisos ambientales caducados o litigios pendientes. Comunidades pueden paralizar fondos en Washington.
                </div>
                <div class="box-highlight">Normas de Desempeño 1 y 7</div>
            </div>
            <div class="grid-box">
                <div class="box-num">Eje 2 • Técnico</div>
                <div class="box-title">Alternativa Ley REP y Compostaje</div>
                <div class="box-desc">
                    El 75 % de los residuos de Osorno es compostable o reciclable. Plantas descentralizadas reducen el volumen y evitan sepultar USD 31M en una megafosa.
                </div>
                <div class="box-highlight">Ley 20.920 • Reducción 75 %</div>
            </div>
            <div class="grid-box">
                <div class="box-num">Eje 3 • Constitucional</div>
                <div class="box-title">Protección y Elusión del SEIA</div>
                <div class="box-desc">
                    Recurso ante la Corte de Valdivia con Orden de No Innovar (ONI) por daño ambiental (Art. 19 N° 8) y denuncia por elusión ante la SMA (Art. 3 letra u).
                </div>
                <div class="box-highlight">Orden de No Innovar Inminente</div>
            </div>
        </div>
    </div>
    <div class="card-footer">
        <span class="source-tag">Análisis Jurídico: Convenio 169 OIT • Marco BID ESPS • Ley N° 19.300</span>
        <span>© 2026 Última Prensa</span>
    </div>
</div>
</body>
</html>
"""

def render_html_to_png(html_content: str, output_png: Path, width=870, height=650):
    temp_html = output_png.with_suffix(".html")
    temp_html.write_text(html_content, encoding="utf-8")
    
    cmd = [
        CHROME_BIN,
        "--headless",
        "--hide-scrollbars",
        "--no-sandbox",
        "--disable-gpu",
        "--force-device-scale-factor=2",
        f"--window-size={width},{height}",
        f"--screenshot={output_png.resolve()}",
        f"file://{temp_html.resolve()}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and output_png.exists():
        size_kb = output_png.stat().st_size // 1024
        print(f"[+] Renderizado con éxito: {output_png.name} ({size_kb} KB)")
        return True
    else:
        print(f"[-] Error al renderizar {output_png.name}: {res.stderr}")
        return False

def upload_image_to_substack(png_path: Path) -> dict:
    print(f"[*] Subiendo {png_path.name} a Substack CDN...")
    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    data_uri = f"data:image/png;base64,{b64}"
    
    payload = json.dumps({"image": data_uri}).encode("utf-8")
    req = urllib.request.Request(
        f"https://{PUBLICATION}.substack.com/api/v1/image",
        data=payload,
        headers={
            "Cookie": f"substack.sid={SUBSTACK_SID}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
    )
    try:
        res = urllib.request.urlopen(req)
        resp_data = json.loads(res.read().decode())
        print(f"[+] Imagen subida a Substack CDN: {resp_data.get('url')}")
        return resp_data
    except Exception as e:
        print(f"[-] Error al subir a Substack: {e}")
        return {}

def main():
    base_dir = Path("reportajes/caso_caducidad_rca_curaco/graficos")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    cuadros = [
        ("cuadro_1_cronologia_forense.png", HTML_CUADRO_1, 870, 720),
        ("cuadro_2_entramado_institucional.png", HTML_CUADRO_2, 870, 520),
        ("cuadro_3_ejes_estrategicos.png", HTML_CUADRO_3, 870, 420),
    ]
    
    manifest = {}
    for filename, html_str, w, h in cuadros:
        png_path = base_dir / filename
        ok = render_html_to_png(html_str, png_path, w, h)
        if ok:
            uploaded = upload_image_to_substack(png_path)
            if uploaded:
                manifest[filename] = uploaded
    
    manifest_path = base_dir / "substack_uploads_cache.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Manifiesto guardado en {manifest_path}")

if __name__ == "__main__":
    main()
