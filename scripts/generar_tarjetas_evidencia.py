#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_tarjetas_evidencia.py — Motor de Evidencia Documental (Estilo Silicon / Carbon)
Última Prensa IA Journalism Kit

Convierte fragmentos textuales de sentencias judiciales, decretos alcaldicios,
actas de concejos municipales y oficios de la CGR en tarjetas visuales de alta
fidelidad (PNG Retina 2x) simulando terminales y visores forenses de documentos.
"""

import os
import sys
import subprocess
from pathlib import Path

CHROME_BIN = "/home/pablo/.cache/puppeteer/chrome/linux-153.0.8010.36/chrome-linux64/chrome"
if not os.path.exists(CHROME_BIN):
    CHROME_BIN = "/home/pablo/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    margin: 0;
    padding: 0;
    background: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    -webkit-font-smoothing: antialiased;
    width: 840px;
}}

.window-frame {{
    width: 840px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    overflow: hidden;
    position: relative;
}}

.window-header {{
    background: #f8fafc;
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e2e8f0;
}}

.window-controls {{
    display: flex;
    gap: 8px;
    align-items: center;
}}

.control-dot {{
    width: 11px;
    height: 11px;
    border-radius: 50%;
}}
.dot-red {{ background: #ef4444; }}
.dot-yellow {{ background: #f59e0b; }}
.dot-green {{ background: #10b981; }}

.window-title {{
    font-size: 11px;
    font-weight: 700;
    color: #475569;
    letter-spacing: 1px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.stamp-badge {{
    background: #fee2e2;
    border: 1px solid #fca5a5;
    color: #b91c1c;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}}

.window-body {{
    padding: 22px 26px;
    color: #1e293b;
    font-size: 13.5px;
    line-height: 1.7;
    position: relative;
    background: #ffffff;
}}

.line-wrapper {{
    display: flex;
    gap: 16px;
    margin-bottom: 6px;
}}

.line-number {{
    color: #94a3b8;
    font-size: 12px;
    user-select: none;
    text-align: right;
    width: 28px;
    flex-shrink: 0;
}}

.line-content {{
    flex: 1;
    color: #1e293b;
}}

.hl-highlight {{
    background: #fef3c7;
    color: #92400e;
    padding: 1px 4px;
    border-radius: 3px;
    font-weight: 700;
}}

.hl-alert {{
    background: #fee2e2;
    color: #991b1b;
    padding: 1px 4px;
    border-radius: 3px;
    font-weight: 700;
}}

.hl-cyan {{
    color: #0284c7;
    font-weight: 700;
}}

.window-footer {{
    background: #f8fafc;
    padding: 12px 20px;
    border-top: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11px;
    color: #64748b;
}}

.footer-source {{
    display: flex;
    align-items: center;
    gap: 6px;
}}

.footer-brand {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    color: #d9381e;
    letter-spacing: 0.8px;
}}
</style>
</head>
<body>
<div class="window-frame">
    <div class="window-header">
        <div class="window-controls">
            <span class="control-dot dot-red"></span>
            <span class="control-dot dot-yellow"></span>
            <span class="control-dot dot-green"></span>
        </div>
        <div class="window-title">
            <span>{header_title}</span>
        </div>
        <div class="stamp-badge">{badge_text}</div>
    </div>
    <div class="window-body">
        {lines_html}
    </div>
    <div class="window-footer">
        <div class="footer-source">
            <span>⚖️ <strong>Origen:</strong> {source_text}</span>
        </div>
        <div class="footer-brand">ÚLTIMA PRENSA • EVIDENCIA FORENSE</div>
    </div>
</div>
</body>
</html>"""


EVIDENCIAS_CURACO = [
    {
        "id": "evidencia_1_considerando_60",
        "header_title": "PJUD • 2° JDO. LETRAS OSORNO • ROL C-351-2019",
        "badge_text": "CONFESIÓN BAJO JURAMENTO",
        "source_text": "Sentencia Definitiva 10/06/2020, Considerando 60°, Foja 184",
        "width": 840,
        "height": 460,
        "lines": [
            "// TESTIMONIO DE FUNCIONARIOS MUNICIPALES (DOM OSORNO)",
            "CONSIDERANDO 60°: Que, la testigo doña Andrea Coral Peña declara:",
            "«El señor Mario Mora Mora (inspector técnico municipal) informó",
            "que <span class='hl-alert'>el terreno de Curaco presentaba suelos alofánicos</span> con alta",
            "sensitividad y riesgo de colapso, según el estudio de Arcadis 2007».",
            "",
            "«Dicho informe <span class='hl-alert'>NO FUE ENTREGADO a los oferentes</span> en la licitación.",
            "La Municipalidad optó por licitar con los datos de Lab-Sur Ltda.,",
            "pese a que sabían que <span class='hl-highlight'>no resistía obras pesadas sin licuarse</span>».",
            "",
            "RESOLUCIÓN DEL TRIBUNAL: Queda judicialmente acreditado que el",
            "Municipio de Osorno <span class='hl-cyan'>ocultó información geotécnica esencial</span> al Fisco."
        ]
    },
    {
        "id": "evidencia_2_decreto_300",
        "header_title": "DECRETO ALCALDICIO N° 300 • I. MUNICIPALIDAD DE OSORNO",
        "badge_text": "ACTO ILEGAL DETERMINANTE",
        "source_text": "Decreto Alcaldicio 10/01/2020 y Considerando 54° de la Sentencia",
        "width": 840,
        "height": 460,
        "lines": [
            "// DECRETO ALCALDICIO FIRMADO POR JAIME BERTÍN VALENZUELA",
            "DECRETO N° 300: «Póngase término anticipado e intempestivo al",
            "contrato de obras del Relleno Sanitario Curaco con Servitrans S.A.»",
            "",
            "CONSIDERANDO 54° (Tribunal Civil de Osorno):",
            "«El Decreto N° 300 dictado por el Alcalde <span class='hl-alert'>invadió competencias exclusivas</span>",
            "del Poder Judicial al resolver el contrato encontrándose el juicio ya radicado.",
            "Dicha infracción <span class='hl-highlight'>anuló toda defensa patrimonial del Municipio</span>».",
            "",
            "RESULTADO PATRIMONIAL INAPELABLE:",
            "Condena al Municipio a pagar <span class='hl-cyan'>$3.177.732.167 de pesos</span> a Servitrans."
        ]
    },
    {
        "id": "evidencia_3_querella_sii_facturas",
        "header_title": "TRIBUNAL DE GARANTÍA • QUERELLA CRIMINAL SII",
        "badge_text": "ACCIÓN PENAL TRIBUTARIA",
        "source_text": "Servicio de Impuestos Internos contra Ciudad Limpia S.A. (Abril 2025)",
        "width": 840,
        "height": 460,
        "lines": [
            "// QUERELLA CRIMINAL POR DELITO TRIBUTARIO (ART. 97 N° 4 CÓD. TRIB.)",
            "SUJETO: Representantes legales de Ciudad Limpia S.A. (ex Servitrans)",
            "RUT: 76.377.430-9 (Mismo adjudicatario de los $24.000 millones)",
            "",
            "IMPUTACIÓN FORMAL:",
            "«Incorporación reiterada de <span class='hl-alert'>facturas falsas y documentos sin respaldo</span>",
            "comercial efectivo con el objeto de rebajar artificialmente el débito fiscal».",
            "",
            "ESTADO PROCESAL:",
            "Causa remitida al <span class='hl-cyan'>Ministerio Público</span> para peritajes de la Brigada",
            "de Delitos Económicos (BRIDEC) de la Policía de Investigaciones."
        ]
    }
]


def render_evidence_cards(output_dir: Path) -> list:
    """Renderiza tarjetas de evidencia textual judicial y forense estilo Silicon a PNG Retina 2x."""
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "temp_html"
    temp_dir.mkdir(parents=True, exist_ok=True)

    rendered_files = []

    for item in EVIDENCIAS_CURACO:
        card_id = item["id"]
        html_file = temp_dir / f"{card_id}.html"
        png_file = output_dir / f"{card_id}.png"

        # Formatear líneas
        lines_html_list = []
        for idx, line in enumerate(item["lines"], start=1):
            line_str = line if line else "&nbsp;"
            lines_html_list.append(
                f'<div class="line-wrapper">'
                f'<span class="line-number">{idx:02d}</span>'
                f'<span class="line-content">{line_str}</span>'
                f'</div>'
            )
        lines_html = "\n".join(lines_html_list)

        html_content = HTML_TEMPLATE.format(
            header_title=item["header_title"],
            badge_text=item["badge_text"],
            source_text=item["source_text"],
            lines_html=lines_html
        )

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Renderizando {card_id} a PNG Retina 2x ({item['width']}x{item['height']})...")
        cmd = [
            CHROME_BIN,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--force-device-scale-factor=2",
            f"--window-size={item['width']},{item['height']}",
            f"--screenshot={png_file}",
            f"file://{html_file.resolve()}"
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and png_file.exists():
            print(f"  ✓ {png_file.name} generado con éxito ({png_file.stat().st_size // 1024} KB)")
            rendered_files.append(png_file)
        else:
            print(f"  ✗ Error al renderizar {card_id}: {res.stderr}")

    return rendered_files


if __name__ == "__main__":
    out_dir = Path("reportajes/caso_relleno_curaco_osorno/graficos")
    pngs = render_evidence_cards(out_dir)
    print(f"\nGeneración de tarjetas de evidencia finalizada: {len(pngs)} tarjetas listas.")
