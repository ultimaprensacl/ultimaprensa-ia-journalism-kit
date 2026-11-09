#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_cuadros_bonos_afp.py
Genera infografías y tablas forenses de alta resolución (2x Retina) para el reportaje
de Bonos Ejecutivos AFP y el desplome del Fondo E, las renderiza con Headless Chrome
y las sube automáticamente al CDN oficial de Substack.
"""

import os
import json
import base64
import subprocess
import urllib.request
from pathlib import Path

# Cargar variables desde n8n/.env si existen
env_file = Path(__file__).resolve().parent.parent.parent / "n8n" / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

CHROME_BIN = "/home/pablo/.cache/puppeteer/chrome/linux-153.0.8010.36/chrome-linux64/chrome"
if not os.path.exists(CHROME_BIN):
    CHROME_BIN = "/home/pablo/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"

SUBSTACK_SID = os.environ.get("SUBSTACK_SID", "")
PUBLICATION = os.environ.get("SUBSTACK_SUBDOMAIN", "ultimaprensacl")

CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: #f1f5f9;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 20px;
    -webkit-font-smoothing: antialiased;
}

.card {
    width: 1120px;
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
    padding: 6px 12px;
    border-radius: 6px;
    white-space: nowrap;
}

.card-body {
    padding: 22px 26px;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.8px;
    line-height: 1.45;
}

th {
    background: #f8fafc;
    color: #1e293b;
    font-weight: 800;
    text-align: left;
    padding: 10px 12px;
    border-bottom: 2px solid #cbd5e1;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

td {
    padding: 10px 12px;
    border-bottom: 1px solid #e2e8f0;
    color: #334155;
    vertical-align: middle;
}

tr:nth-child(even) {
    background: #f8fafc;
}

tr.total-row {
    background: #0f172a !important;
    color: #ffffff !important;
    font-weight: 800;
}

tr.total-row td {
    color: #ffffff !important;
    border-top: 2px solid #d9381e;
    border-bottom: none;
    padding: 12px 12px;
    font-size: 13px;
}

.mono {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    white-space: nowrap;
}

.highlight-red {
    color: #b91c1c;
    font-weight: 800;
    background: #fef2f2;
    padding: 3px 7px;
    border-radius: 4px;
    border: 1px solid #fecaca;
    display: inline-block;
}

.highlight-green {
    color: #047857;
    font-weight: 800;
    background: #ecfdf5;
    padding: 3px 7px;
    border-radius: 4px;
    border: 1px solid #a7f3d0;
    display: inline-block;
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
    font-weight: 600;
}

.flow-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
}

.flow-step {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-top: 4px solid #0f172a;
    border-radius: 10px;
    padding: 14px 12px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.flow-step.danger {
    border-top-color: #d9381e;
    background: #fff5f5;
    border-color: #fecaca;
}

.step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px;
    font-weight: 800;
    color: #d9381e;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.step-title {
    font-size: 13.5px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
    line-height: 1.3;
}

.step-desc {
    font-size: 12px;
    color: #475569;
    line-height: 1.45;
    margin-bottom: 10px;
}

.step-metric {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    font-weight: 700;
    background: #0f172a;
    color: #ffffff;
    padding: 5px 8px;
    border-radius: 5px;
    text-align: center;
}

.flow-step.danger .step-metric {
    background: #d9381e;
}
"""

HTML_CUADRO_1 = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><style>{CSS_BASE}</style></head>
<body>
<div class="card">
    <div class="card-header">
        <div class="card-title-group">
            <h2>Mecanismo de Asimetría y Riesgo Moral en los Derivados de las AFP</h2>
            <p>Secuencia cronológica: de la ganancia contable en papel al cobro de bonos en efectivo y el desplome del Fondo E</p>
        </div>
        <span class="badge">Esquema Forense • Última Prensa</span>
    </div>
    <div class="card-body">
        <div class="flow-grid">
            <div class="flow-step">
                <div>
                    <div class="step-num">Fase 1 • 31 Dic 2025</div>
                    <div class="step-title">Foto Contable en Papel</div>
                    <div class="step-desc">Valorización transitoria mark-to-market en contratos swaps de tasas foráneas e inflación del Encaje corporativo.</div>
                </div>
                <div class="step-metric">+US$ 1.400 Millones</div>
            </div>
            <div class="flow-step">
                <div>
                    <div class="step-num">Fase 2 • Ene-Mar 2026</div>
                    <div class="step-title">Apertura de Bóveda</div>
                    <div class="step-desc">Comités y directorios aprueban bonos anuales sobre la foto contable de diciembre. Alzas de +27 % a +112 %.</div>
                </div>
                <div class="step-metric">$8.113M en Bonos</div>
            </div>
            <div class="flow-step">
                <div>
                    <div class="step-num">Fase 3 • 1T 2026</div>
                    <div class="step-title">Blindaje Bancario</div>
                    <div class="step-desc">Transferencia en efectivo a cuentas personales de la alta gerencia dentro de un pozo salarial récord de la industria.</div>
                </div>
                <div class="step-metric">$38.624M Pagados</div>
            </div>
            <div class="flow-step danger">
                <div>
                    <div class="step-num">Fase 4 • Ago-Sep 2026</div>
                    <div class="step-title">Colapso del Fondo E</div>
                    <div class="step-desc">Rebote de tasas en EE. UU. revierte los swaps. Desplome histórico de -10,39 % real (-4,92 % solo en septiembre).</div>
                </div>
                <div class="step-metric">-US$ 11.600 Millones</div>
            </div>
            <div class="flow-step danger">
                <div>
                    <div class="step-num">Fase 5 • Impunidad Legal</div>
                    <div class="step-title">Cero Devolución</div>
                    <div class="step-desc">Ausencia de cláusulas clawback en el D.L. N.° 3.500. Ejecutivos retienen el 100 % de sus bonos y afiliados asumen la pérdida.</div>
                </div>
                <div class="step-metric">$0 Restituido</div>
            </div>
        </div>
    </div>
    <div class="card-footer">
        <span>Fuente: Estados Financieros IFRS (CMF / Superintendencia de Pensiones) • NIC 24 y D.L. N.° 3.500</span>
        <span>Unidad de Investigación • Última Prensa</span>
    </div>
</div>
</body>
</html>
"""

HTML_CUADRO_2 = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><style>{CSS_BASE}</style></head>
<body>
<div class="card">
    <div class="card-header">
        <div class="card-title-group">
            <h2>Radiografía del Gasto en Alta Dirección en las 7 Administradoras (Norma NIC 24)</h2>
            <p>Desglose de remuneraciones fijas, bonos variables e indemnizaciones pagadas al personal clave de la gerencia</p>
        </div>
        <span class="badge">Evidencia IFRS • CMF / SP</span>
    </div>
    <div class="card-body">
        <table>
            <thead>
                <tr>
                    <th>Administradora</th>
                    <th>Salarios Base Fijos</th>
                    <th>Bonos e Incentivos Variables</th>
                    <th>Indemnizaciones y Otros</th>
                    <th>Total Personal Clave</th>
                    <th>Peso</th>
                    <th>Dotación Ejecutiva Informada</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>AFP Provida S.A.</strong></td>
                    <td class="mono">$5.325.132.000</td>
                    <td class="mono"><span class="highlight-red">$2.290.470.000</span><br/><small>($2.114M resultados + $176M c/p)</small></td>
                    <td class="mono">$1.155.094.000</td>
                    <td class="mono"><strong>$8.770.695.000</strong></td>
                    <td class="mono"><strong>22,7 %</strong></td>
                    <td>78 directivos (16 gerentes, 10 subgerentes, 52 jefes)</td>
                </tr>
                <tr>
                    <td><strong>AFP Capital S.A.</strong></td>
                    <td class="mono">$4.573.655.000</td>
                    <td class="mono"><span class="highlight-red">$3.104.211.000</span><br/><small>(Bonos desempeño / corto plazo)</small></td>
                    <td class="mono">$536.276.000</td>
                    <td class="mono"><strong>$8.214.142.000</strong></td>
                    <td class="mono"><strong>21,3 %</strong></td>
                    <td>Plana gerencial y jefaturas (+50,4 % anual)</td>
                </tr>
                <tr>
                    <td><strong>AFP Habitat S.A.</strong></td>
                    <td class="mono">$5.126.341.000</td>
                    <td class="mono"><span class="highlight-red">$2.718.557.000</span><br/><small>(Incentivos metas corporativas)</small></td>
                    <td class="mono">$328.400.000</td>
                    <td class="mono"><strong>$8.173.298.000</strong></td>
                    <td class="mono"><strong>21,2 %</strong></td>
                    <td>~55 ejecutivos (17-19 gerentes, 34-43 subgerentes)</td>
                </tr>
                <tr>
                    <td><strong>AFP Modelo S.A.</strong></td>
                    <td class="mono">$4.422.360.000</td>
                    <td class="mono">Integrado en asignaciones</td>
                    <td class="mono">$0</td>
                    <td class="mono"><strong>$4.422.360.000</strong></td>
                    <td class="mono"><strong>11,4 %</strong></td>
                    <td>61 ejecutivos (19 gerentes, 42 subgerentes)</td>
                </tr>
                <tr>
                    <td><strong>AFP Cuprum S.A.</strong></td>
                    <td class="mono">$3.970.288.000</td>
                    <td class="mono">$118.496.000</td>
                    <td class="mono">$5.652.000</td>
                    <td class="mono"><strong>$4.094.436.000</strong></td>
                    <td class="mono"><strong>10,6 %</strong></td>
                    <td>Gerentes y principales ejecutivos</td>
                </tr>
                <tr>
                    <td><strong>AFP Planvital S.A.</strong></td>
                    <td class="mono">$2.544.801.000</td>
                    <td class="mono">Integrado en asignaciones</td>
                    <td class="mono">$121.617.000</td>
                    <td class="mono"><strong>$2.666.418.000</strong></td>
                    <td class="mono"><strong>6,9 %</strong></td>
                    <td>Gerentes, fiscal, contralor y cumplimiento</td>
                </tr>
                <tr>
                    <td><strong>AFP Uno S.A.</strong></td>
                    <td class="mono">$2.283.185.000</td>
                    <td class="mono">Integrado en asignaciones</td>
                    <td class="mono">$0</td>
                    <td class="mono"><strong>$2.283.185.000</strong></td>
                    <td class="mono"><strong>5,9 %</strong></td>
                    <td>Cargos con potestad de planificación y control</td>
                </tr>
                <tr class="total-row">
                    <td>TOTAL SISTEMA (7 AFP)</td>
                    <td class="mono">$28.245.762.000</td>
                    <td class="mono">$8.113.238.000+ (3 mayores)</td>
                    <td class="mono">$2.147.039.000</td>
                    <td class="mono">$38.624.534.000</td>
                    <td class="mono">100,0 %</td>
                    <td>Cúpula de alta dirección previsional</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="card-footer">
        <span>Fuente: Notas Explicativas de Partes Relacionadas (NIC 24) en Estados Financieros Auditados (CMF / SP)</span>
        <span>Unidad de Investigación • Última Prensa</span>
    </div>
</div>
</body>
</html>
"""

HTML_CUADRO_3 = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><style>{CSS_BASE}</style></head>
<body>
<div class="card">
    <div class="card-header">
        <div class="card-title-group">
            <h2>El Botín de las Controladoras: $1,13 Billones en Comisiones y $566.869 Millones en Utilidades</h2>
            <p>Estados de Resultados Integrales Auditados (Códigos 31.11.010, 31.11.020 y 31.11.300 de la Superintendencia de Pensiones)</p>
        </div>
        <span class="badge">Balances Auditados • 7 AFP</span>
    </div>
    <div class="card-body">
        <table>
            <thead>
                <tr>
                    <th>Administradora</th>
                    <th>Controlador Principal</th>
                    <th>Comisiones Cobradas (31.11.010)</th>
                    <th>Utilidad Encaje Total (31.11.020)</th>
                    <th>Encaje Fondo E (31.11.025)</th>
                    <th>Utilidad Líquida Final (31.11.300)</th>
                    <th>Margen Neto</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>AFP Provida S.A.</strong></td>
                    <td>MetLife Inc. (EE. UU.)</td>
                    <td class="mono">$264.735.572.000</td>
                    <td class="mono">+$27.612.061.000</td>
                    <td class="mono">+$1.726.116.000</td>
                    <td class="mono"><span class="highlight-green">$129.398.125.000</span></td>
                    <td class="mono"><strong>48,88 %</strong></td>
                </tr>
                <tr>
                    <td><strong>AFP Habitat S.A.</strong></td>
                    <td>ILC / Prudential (EE. UU.)</td>
                    <td class="mono">$251.522.594.000</td>
                    <td class="mono">+$40.444.931.000</td>
                    <td class="mono">+$2.594.694.000</td>
                    <td class="mono"><span class="highlight-green">$140.145.938.000</span></td>
                    <td class="mono"><strong>55,72 %</strong></td>
                </tr>
                <tr>
                    <td><strong>AFP Capital S.A.</strong></td>
                    <td>Sura Asset Management</td>
                    <td class="mono">$205.892.506.000</td>
                    <td class="mono">+$26.195.554.000</td>
                    <td class="mono">+$2.018.055.000</td>
                    <td class="mono"><span class="highlight-green">$102.713.160.000</span></td>
                    <td class="mono"><strong>49,89 %</strong></td>
                </tr>
                <tr>
                    <td><strong>AFP Cuprum S.A.</strong></td>
                    <td>Principal Financial (EE. UU.)</td>
                    <td class="mono">$165.121.769.000</td>
                    <td class="mono">+$26.925.461.000</td>
                    <td class="mono">+$1.888.716.000</td>
                    <td class="mono"><span class="highlight-green">$79.040.624.000</span></td>
                    <td class="mono"><strong>47,87 %</strong></td>
                </tr>
                <tr>
                    <td><strong>AFP Planvital S.A.</strong></td>
                    <td>Assicurazioni Generali (Italia)</td>
                    <td class="mono">$119.823.071.000</td>
                    <td class="mono">+$8.070.120.000</td>
                    <td class="mono">+$573.732.000</td>
                    <td class="mono"><span class="highlight-green">$53.179.503.000</span></td>
                    <td class="mono"><strong>44,38 %</strong></td>
                </tr>
                <tr>
                    <td><strong>AFP Modelo S.A.</strong></td>
                    <td>Grupo Navarro (Atlántico)</td>
                    <td class="mono">$103.165.909.000</td>
                    <td class="mono">+$11.661.735.000</td>
                    <td class="mono">+$791.296.000</td>
                    <td class="mono"><span class="highlight-green">$53.126.727.000</span></td>
                    <td class="mono"><strong>51,50 %</strong></td>
                </tr>
                <tr>
                    <td><strong>AFP Uno S.A.</strong></td>
                    <td>Tanza SpA</td>
                    <td class="mono">$25.189.370.000</td>
                    <td class="mono">+$1.718.992.000</td>
                    <td class="mono">+$110.322.000</td>
                    <td class="mono"><span class="highlight-green">$9.265.163.000</span></td>
                    <td class="mono"><strong>36,78 %</strong></td>
                </tr>
                <tr class="total-row">
                    <td>TOTAL INDUSTRIA</td>
                    <td>7 Administradoras</td>
                    <td class="mono">$1.135.450.791.000</td>
                    <td class="mono">+$142.628.854.000</td>
                    <td class="mono">+$9.702.931.000</td>
                    <td class="mono">$566.869.240.000</td>
                    <td class="mono">49,92 %</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="card-footer">
        <span>Fuente: Estados de Resultados Integrales Auditados bajo norma IFRS (CMF / Superintendencia de Pensiones)</span>
        <span>Unidad de Investigación • Última Prensa</span>
    </div>
</div>
</body>
</html>
"""


def render_html_to_png(html_content: str, output_png: Path, width: int = 1160, height: int = 1000) -> bool:
    temp_html = output_png.with_suffix(".html")
    temp_html.write_text(html_content, encoding="utf-8")

    cmd = [
        CHROME_BIN,
        "--headless",
        "--hide-scrollbars",
        "--no-sandbox",
        "--disable-gpu",
        "--force-device-scale-factor=3.5",
        f"--window-size={width},{height}",
        f"--screenshot={output_png.resolve()}",
        f"file://{temp_html.resolve()}",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and output_png.exists():
        try:
            from PIL import Image, ImageChops
            img = Image.open(output_png).convert("RGB")
            bg = Image.new("RGB", img.size, img.getpixel((0, img.height - 1)))
            diff = ImageChops.difference(img, bg)
            bbox = diff.getbbox()
            if bbox:
                crop_bottom = min(img.height, bbox[3] + 70)
                img.crop((0, 0, img.width, crop_bottom)).save(output_png)
        except Exception:
            pass
        size_kb = output_png.stat().st_size // 1024
        print(f"[+] Renderizado 4K Ultra-HD exitoso: {output_png.name} ({size_kb} KB)")
        return True
    print(f"[-] Error al renderizar {output_png.name}: {res.stderr}")
    return False


def upload_image_to_substack(png_path: Path) -> dict:
    print(f"[*] Subiendo {png_path.name} al CDN de Substack...")
    with open(png_path, "rb") as f:
        raw_bytes = f.read()
        b64 = base64.b64encode(raw_bytes).decode("utf-8")
    data_uri = f"data:image/png;base64,{b64}"

    payload = json.dumps({"image": data_uri}).encode("utf-8")
    req = urllib.request.Request(
        f"https://{PUBLICATION}.substack.com/api/v1/image",
        data=payload,
        headers={
            "Cookie": f"substack.sid={SUBSTACK_SID}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0",
            "Origin": f"https://{PUBLICATION}.substack.com",
            "Referer": f"https://{PUBLICATION}.substack.com/publish",
        },
    )
    try:
        res = urllib.request.urlopen(req, timeout=45)
        resp_data = json.loads(res.read().decode("utf-8"))
        resp_data["bytes"] = len(raw_bytes)
        print(f"[+] Subida exitosa a Substack CDN: {resp_data.get('url')}")
        return resp_data
    except Exception as e:
        print(f"[-] Error al subir {png_path.name} a Substack: {e}")
        return {}


def main():
    base_dir = Path("reportajes/Bonos Ejecutivos AFP/graficos")
    base_dir.mkdir(parents=True, exist_ok=True)

    cuadros = [
        ("cuadro_1_flujo_bonos_swaps.png", HTML_CUADRO_1, 1160, 600),
        ("cuadro_2_remuneraciones_7_afp.png", HTML_CUADRO_2, 1160, 1050),
        ("cuadro_3_botin_comisiones_utilidades_afp.png", HTML_CUADRO_3, 1160, 1000),
    ]

    manifest = {}
    for filename, html_str, w, h in cuadros:
        png_path = base_dir / filename
        if render_html_to_png(html_str, png_path, w, h):
            uploaded = upload_image_to_substack(png_path)
            if uploaded:
                manifest[filename] = uploaded

    manifest_path = base_dir / "substack_uploads_cache.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Manifiesto CDN guardado en: {manifest_path}")


if __name__ == "__main__":
    main()

