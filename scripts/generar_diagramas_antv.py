#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_diagramas_antv.py — Motor de Diagramas Vectoriales e Infográficos (Estilo AntV / D3)
Última Prensa IA Journalism Kit

Genera diagramas vectoriales estructurados (SVG y PNG Retina 2x) para mapear
flujos financieros de contratación pública, redes de actores y árboles de causalidad.
"""

import os
import sys
import subprocess
from pathlib import Path

CHROME_BIN = "/home/pablo/.cache/puppeteer/chrome/linux-153.0.8010.36/chrome-linux64/chrome"
if not os.path.exists(CHROME_BIN):
    CHROME_BIN = "/home/pablo/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"

DIAGRAMA_FLUJO_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    margin: 0;
    padding: 0;
    background: #ffffff;
    font-family: 'Plus Jakarta Sans', sans-serif;
    -webkit-font-smoothing: antialiased;
    width: 840px;
}

.diagram-card {
    width: 840px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px 28px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    color: #0f172a;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f1f5f9;
}

.brand {
    font-size: 11px;
    font-weight: 800;
    color: #d9381e;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.title {
    font-size: 19px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}

.subtitle {
    font-size: 12.5px;
    color: #64748b;
    margin-bottom: 18px;
}

/* SVG Container */
.svg-container {
    width: 100%;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px;
}

.node-rect {
    rx: 8;
    ry: 8;
    transition: all 0.3s;
}

.node-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px;
    font-weight: 700;
    fill: #0f172a;
}

.node-desc {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
}

.link-line {
    stroke-dasharray: 6, 6;
    animation: flow 20s linear infinite;
}

.footer {
    display: flex;
    justify-content: space-between;
    margin-top: 16px;
    font-size: 11px;
    color: #64748b;
}
</style>
</head>
<body>
<div class="diagram-card">
    <div class="header">
        <div class="brand">AntV • Diagrama de Flujo y Malla Financiera</div>
        <div style="font-size: 11px; color: #64748b; font-weight: 700;">AUDITORÍA PATRIMONIAL</div>
    </div>
    <div class="title">Ruta del Dinero en Curaco: El Doble Negocio de la Basura</div>
    <div class="subtitle">Evolución de los fondos públicos desde el colapso judicial ($1.840M) hasta el megacontrato de recolección ($24.000M).</div>
    
    <div class="svg-container">
        <svg viewBox="0 0 780 340" width="100%" height="340" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="gradRed" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#b91c1c"/>
                    <stop offset="100%" stop-color="#991b1b"/>
                </linearGradient>
                <linearGradient id="gradAmber" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#d97706"/>
                    <stop offset="100%" stop-color="#b45309"/>
                </linearGradient>
                <linearGradient id="gradCyan" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#0284c7"/>
                    <stop offset="100%" stop-color="#0369a1"/>
                </linearGradient>
                <linearGradient id="gradEmerald" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#059669"/>
                    <stop offset="100%" stop-color="#047857"/>
                </linearGradient>
                <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 8 5 L 0 9 z" fill="#64748b"/>
                </marker>
                <marker id="arrowRed" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 8 5 L 0 9 z" fill="#ef4444"/>
                </marker>
                <marker id="arrowGreen" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 8 5 L 0 9 z" fill="#10b981"/>
                </marker>
            </defs>

            <!-- Conectores Flujo 1: Indemnización Judicial -->
            <path d="M 210 70 L 330 70" stroke="#ef4444" stroke-width="2.5" marker-end="url(#arrowRed)" fill="none"/>
            <path d="M 490 70 L 590 70" stroke="#ef4444" stroke-width="2.5" marker-end="url(#arrowRed)" fill="none"/>

            <!-- Conectores Flujo 2: Megacontrato Licitación -->
            <path d="M 210 230 L 330 230" stroke="#10b981" stroke-width="2.5" marker-end="url(#arrowGreen)" fill="none"/>
            <path d="M 490 230 L 590 230" stroke="#10b981" stroke-width="2.5" marker-end="url(#arrowGreen)" fill="none"/>

            <!-- Enlace vertical: Mutación Societaria (9 días) -->
            <path d="M 670 120 L 670 180" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="5,5" fill="none"/>
            <rect x="610" y="135" width="120" height="26" rx="4" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
            <text x="670" y="152" fill="#b45309" font-size="10" font-weight="800" text-anchor="middle">MUTACIÓN: 9 DÍAS</text>

            <!-- NODO 1: Municipio Osorno (Erario) -->
            <g transform="translate(40, 35)">
                <rect class="node-rect" width="170" height="70" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
                <text class="node-title" x="85" y="28" fill="#1e293b" text-anchor="middle">Municipalidad Osorno</text>
                <text class="node-desc" x="85" y="50" fill="#64748b" text-anchor="middle">Demandada C-351-2019</text>
            </g>

            <!-- NODO 2: Fallo y Transacción -->
            <g transform="translate(330, 35)">
                <rect class="node-rect" width="160" height="70" fill="#fef2f2" stroke="#f87171" stroke-width="1.5"/>
                <text class="node-title" x="80" y="28" fill="#991b1b" text-anchor="middle">Fallo Corte Suprema</text>
                <text class="node-desc" x="80" y="50" fill="#dc2626" text-anchor="middle">$1.480M + $360M Boleta</text>
            </g>

            <!-- NODO 3: Servitrans S.A. -->
            <g transform="translate(590, 35)">
                <rect class="node-rect" width="160" height="70" fill="#ffffff" stroke="#f87171" stroke-width="1.5"/>
                <text class="node-title" x="80" y="28" fill="#991b1b" text-anchor="middle">Servitrans S.A.</text>
                <text class="node-desc" x="80" y="50" fill="#dc2626" text-anchor="middle">Cobro >$6.300M Total</text>
            </g>

            <!-- NODO 4: Licitación 2023 -->
            <g transform="translate(40, 195)">
                <rect class="node-rect" width="170" height="70" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
                <text class="node-title" x="85" y="28" fill="#1e293b" text-anchor="middle">Mercado Público</text>
                <text class="node-desc" x="85" y="50" fill="#0284c7" text-anchor="middle">ID 2308-97-LR23</text>
            </g>

            <!-- NODO 5: Contrato Concesión -->
            <g transform="translate(330, 195)">
                <rect class="node-rect" width="160" height="70" fill="#f0fdf4" stroke="#4ade80" stroke-width="1.5"/>
                <text class="node-title" x="80" y="28" fill="#14532d" text-anchor="middle">Megacontrato 5 Años</text>
                <text class="node-desc" x="80" y="50" fill="#16a34a" text-anchor="middle">$23.964M ($399M/mes)</text>
            </g>

            <!-- NODO 6: Ciudad Limpia S.A. -->
            <g transform="translate(590, 195)">
                <rect class="node-rect" width="160" height="70" fill="#ffffff" stroke="#4ade80" stroke-width="1.5"/>
                <text class="node-title" x="80" y="28" fill="#14532d" text-anchor="middle">«Ciudad Limpia S.A.»</text>
                <text class="node-desc" x="80" y="50" fill="#16a34a" text-anchor="middle">RUT 76.377.430-9 (SII)</text>
            </g>
        </svg>
    </div>

    <div class="footer">
        <div>Fuente: Segundo Juzgado de Letras de Osorno, Mercado Público y Registro de Empresas y Sociedades.</div>
        <div style="font-weight: 700; color: #d9381e;">ÚLTIMA PRENSA • DATA JOURNALISM</div>
    </div>
</div>
</body>
</html>"""


def render_antv_diagram(output_dir: Path):
    """Renderiza el diagrama vectorial de flujo de fondos a SVG y PNG Retina 2x."""
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "temp_html"
    temp_dir.mkdir(parents=True, exist_ok=True)

    html_file = temp_dir / "diagrama_flujo_curaco.html"
    png_file = output_dir / "diagrama_flujo_curaco.png"
    svg_file = output_dir / "diagrama_flujo_curaco.svg"

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(DIAGRAMA_FLUJO_HTML)

    print(f"Renderizando diagrama vectorial AntV a PNG Retina 2x (880x620)...")
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--force-device-scale-factor=2",
        "--window-size=920,620",
        f"--screenshot={png_file}",
        f"file://{html_file.resolve()}"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and png_file.exists():
        print(f"  ✓ {png_file.name} generado con éxito ({png_file.stat().st_size // 1024} KB)")
    else:
        print(f"  ✗ Error al renderizar diagrama: {res.stderr}")

    # Extraer el SVG puro para uso vectorial directo
    svg_start = DIAGRAMA_FLUJO_HTML.find("<svg")
    svg_end = DIAGRAMA_FLUJO_HTML.find("</svg>") + 6
    if svg_start != -1 and svg_end != -1:
        svg_content = DIAGRAMA_FLUJO_HTML[svg_start:svg_end]
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content)
        print(f"  ✓ {svg_file.name} exportado como SVG vectorial nativo.")


if __name__ == "__main__":
    out_dir = Path("reportajes/caso_relleno_curaco_osorno/graficos")
    render_antv_diagram(out_dir)
    print("\nGeneración de diagramas vectoriales completada.")
