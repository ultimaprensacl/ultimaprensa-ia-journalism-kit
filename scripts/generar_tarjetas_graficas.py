#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_tarjetas_graficas.py — Generador de Infografías e Infocards para Última Prensa
Convierte datos estructurados y esquemas de investigación en tarjetas gráficas
de alta definición (PNG 2x Retina) y animaciones (GIF/WebP) para Substack y web.
Utiliza Headless Chrome y FFmpeg locales sin dependencias externas pesadas.
"""

import os
import sys
import subprocess
from pathlib import Path

CHROME_BIN = "/home/pablo/.cache/puppeteer/chrome/linux-153.0.8010.36/chrome-linux64/chrome"
if not os.path.exists(CHROME_BIN):
    CHROME_BIN = "/home/pablo/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"

BASE_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: #090d16;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 30px;
    -webkit-font-smoothing: antialiased;
}

.card-wrapper {
    width: 780px;
    background: linear-gradient(145deg, #111726 0%, #0c101b 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px;
    padding: 32px 36px;
    box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.05);
    color: #f1f5f9;
    position: relative;
    overflow: hidden;
}

.card-wrapper::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #d9381e, #f97316, #eab308, #3b82f6);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #d9381e;
}

.brand-badge .dot {
    width: 8px;
    height: 8px;
    background: #d9381e;
    border-radius: 50%;
    box-shadow: 0 0 10px #d9381e;
}

.category-pill {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 0.5px;
}

.card-title {
    font-size: 22px;
    font-weight: 800;
    line-height: 1.3;
    color: #ffffff;
    margin-bottom: 8px;
}

.card-subtitle {
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.5;
    margin-bottom: 24px;
}

/* Timeline Components */
.timeline {
    position: relative;
    padding-left: 28px;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 6px;
    bottom: 12px;
    width: 2px;
    background: linear-gradient(180deg, #d9381e 0%, rgba(217, 56, 30, 0.2) 100%);
}

.timeline-item {
    position: relative;
    margin-bottom: 20px;
}

.timeline-item:last-child {
    margin-bottom: 0;
}

.timeline-node {
    position: absolute;
    left: -28px;
    top: 2px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #0c101b;
    border: 3px solid #d9381e;
    box-shadow: 0 0 12px rgba(217, 56, 30, 0.6);
}

.timeline-date {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    color: #f97316;
    margin-bottom: 4px;
}

.timeline-title {
    font-size: 15px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 4px;
}

.timeline-desc {
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.5;
}

.tag-alert {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
    margin-top: 4px;
}

/* Metric Grid */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-bottom: 20px;
}

.metric-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px 18px;
}

.metric-box.highlight {
    background: rgba(217, 56, 30, 0.08);
    border-color: rgba(217, 56, 30, 0.3);
}

.metric-label {
    font-size: 12px;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 800;
    color: #f8fafc;
}

.metric-value.danger { color: #ef4444; }
.metric-value.warn { color: #f59e0b; }
.metric-value.cyan { color: #38bdf8; }

.metric-note {
    font-size: 11px;
    color: #64748b;
    margin-top: 4px;
}

/* Big Alert Callout */
.big-callout {
    background: rgba(249, 115, 22, 0.08);
    border-left: 4px solid #f97316;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin-top: 18px;
}

.big-callout-title {
    font-size: 13px;
    font-weight: 700;
    color: #fb923c;
    margin-bottom: 4px;
}

.big-callout-text {
    font-size: 12px;
    color: #cbd5e1;
    line-height: 1.5;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 24px;
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 11px;
    color: #64748b;
}
"""

TEMPLATES = {
    "tarjeta_1_alertas_geotecnicas": f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>{BASE_STYLE}</style>
</head>
<body>
<div class="card-wrapper">
    <div class="card-header">
        <div class="brand-badge"><span class="dot"></span> Última Prensa · Investigación</div>
        <div class="category-pill">EXPEDIENTE PERICIAL</div>
    </div>
    <div class="card-title">El Mapa de las Alertas Geotécnicas Desoídas en Curaco</div>
    <div class="card-subtitle">Cronología de los 5 estudios técnicos y peritajes que acreditaron la inviabilidad estructural del terreno, desestimados sistemáticamente por las autoridades.</div>
    
    <div class="timeline">
        <div class="timeline-item">
            <div class="timeline-node"></div>
            <div class="timeline-date">Marzo 2007 · Arcadis Geotécnica</div>
            <div class="timeline-title">«Suelo restrictivo para cualquier proyecto civil»</div>
            <div class="timeline-desc">Contratado por la IMO. Detectó suelos alofánicos con sensitividad extrema (20 a 256). <span class="tag-alert">OCULTADO EN LA LICITACIÓN 2014</span></div>
        </div>
        <div class="timeline-item">
            <div class="timeline-node"></div>
            <div class="timeline-date">Febrero 2008 · Sernageomin</div>
            <div class="timeline-title">Alta vulnerabilidad hidrogeológica en la cuenca de Osorno</div>
            <div class="timeline-desc">Advirtió riesgos críticos de contaminación de acuíferos y remoción en masa. Omitido en bases de licitación.</div>
        </div>
        <div class="timeline-item">
            <div class="timeline-node"></div>
            <div class="timeline-date">2014 · Lab-Sur Ltda.</div>
            <div class="timeline-title">El estudio viciado base de la adjudicación</div>
            <div class="timeline-desc">Aseguró soporte sin prospecciones profundas. La justicia lo calificó de «insuficiente e inválido para diseño».</div>
        </div>
        <div class="timeline-item">
            <div class="timeline-node"></div>
            <div class="timeline-date">2015 · Idom Consultores</div>
            <div class="timeline-title">Falla masiva de ladera y colapso de la ingeniería licitada</div>
            <div class="timeline-desc">Constató grieta de 100 m y salto vertical de 2 m a un mes de obras. Recomendó pozos profundos urgentes.</div>
        </div>
        <div class="timeline-item">
            <div class="timeline-node"></div>
            <div class="timeline-date">Junio 2016 · Petrus Geotécnica</div>
            <div class="timeline-title">Desplazamiento por «creep» y validación de la contraparte municipal</div>
            <div class="timeline-desc">Ladera se movió entre 0,5 y 3 m. El consultor de la IMO, Mario Mora, validó que el proyecto era inviable.</div>
        </div>
    </div>

    <div class="card-footer">
        <div>Fuente: Sentencia Rol C-351-2019 (2° J.L. Osorno) / Corte de Valdivia</div>
        <div>ultimaprensa.cl</div>
    </div>
</div>
</body>
</html>""",

    "tarjeta_2_liquidacion_tribunales": f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>{BASE_STYLE}</style>
</head>
<body>
<div class="card-wrapper">
    <div class="card-header">
        <div class="brand-badge"><span class="dot"></span> Última Prensa · Finanzas Públicas</div>
        <div class="category-pill">FALLO JUDICIAL DEFINITIVO</div>
    </div>
    <div class="card-title">Liquidación del Fiasco de Curaco en Tribunales</div>
    <div class="card-subtitle">El costo patrimonial de la rescisión ilegal decretada por la administración de Jaime Bertín y el acuerdo transaccional en la Corte Suprema.</div>
    
    <div class="metric-grid">
        <div class="metric-box">
            <div class="metric-label">Condena en Primera Instancia</div>
            <div class="metric-value danger">$3.177 M</div>
            <div class="metric-note">2° Juzgado de Letras de Osorno (Rol C-351-2019)</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Ratificación Corte Valdivia</div>
            <div class="metric-value warn">100 %</div>
            <div class="metric-note">Corte de Apelaciones Rol 561-2020 confirmada</div>
        </div>
        <div class="metric-box highlight">
            <div class="metric-label">Pago Único Municipal (Finiquito)</div>
            <div class="metric-value warn">$1.480 M</div>
            <div class="metric-note">Efectivo desembolsado por el Concejo Municipal (2022)</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Garantía Devuelta Cesce Chile</div>
            <div class="metric-value cyan">$360 M</div>
            <div class="metric-note">Póliza restituida a Servitrans sin cobro fiscal</div>
        </div>
    </div>

    <div class="big-callout">
        <div class="big-callout-title">BENEFICIO TOTAL ACUMULADO POR LA CONTRATISTA</div>
        <div class="big-callout-text">Sumando los 22 estados de pago cursados y el finiquito de la Suprema, Servitrans percibió <strong>más de $6.300 millones de pesos</strong> del erario público, dejando en Curaco una fosa de 6 metros inundada y cero avance operativo para la provincia.</div>
    </div>

    <div class="card-footer">
        <div>Fuente: Escritura Notarial Rep. N° 5825 / Resolución Corte Suprema Rol 69.455-2021</div>
        <div>ultimaprensa.cl</div>
    </div>
</div>
</body>
</html>""",

    "tarjeta_3_megacontrato_mutacion": f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>{BASE_STYLE}</style>
</head>
<body>
<div class="card-wrapper">
    <div class="card-header">
        <div class="brand-badge"><span class="dot"></span> Última Prensa · Redes Corporativas</div>
        <div class="category-pill">MERCADO PÚBLICO & SII</div>
    </div>
    <div class="card-title">El Megacontrato y la Mutación Societaria</div>
    <div class="card-subtitle">Cómo el mismo Municipio demandado adjudicó a Servitrans el contrato más cuantioso de su historia y el camuflaje previo a debutar en las calles.</div>
    
    <div class="metric-grid">
        <div class="metric-box highlight">
            <div class="metric-label">Monto Total Licitación (60 meses)</div>
            <div class="metric-value warn">~$24.000 M</div>
            <div class="metric-note">Licitación Mercado Público ID: 2308-97-LR23</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Canon Mensual Garantizado</div>
            <div class="metric-value cyan">$399,4 M</div>
            <div class="metric-note">Retiro domiciliario en 56.000 hogares de Osorno</div>
        </div>
    </div>

    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 18px 20px; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div style="font-size: 13px; font-weight: 700; color: #f8fafc;">LA CRONOLOGÍA DEL CAMUFLAJE (RUT: 76.377.430-9)</div>
            <div style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); font-size: 11px; font-weight: 800; padding: 2px 10px; border-radius: 9999px;">PLAZO: 9 DÍAS</div>
        </div>
        <div style="display: flex; gap: 12px; font-size: 12px; color: #cbd5e1; line-height: 1.5;">
            <div style="flex: 1; border-left: 2px solid #38bdf8; padding-left: 10px;">
                <strong style="color: #38bdf8;">23 de abril de 2024</strong><br>
                Servitrans Servicio de Limpieza Urbana S.A. modifica estatutos en notaría y pasa a llamarse <strong>«Ciudad Limpia S.A.»</strong>
            </div>
            <div style="flex: 1; border-left: 2px solid #10b981; padding-left: 10px;">
                <strong style="color: #10b981;">02 de mayo de 2024</strong><br>
                Ciudad Limpia debuta en las calles de Osorno con camiones nuevos, diluyendo ante los vecinos el escándalo de Curaco.
            </div>
        </div>
    </div>

    <div class="big-callout" style="background: rgba(239, 68, 68, 0.08); border-left-color: #ef4444;">
        <div class="big-callout-title" style="color: #f87171;">ARISTA PENAL Y TRIBUTARIA (ABRIL 2025)</div>
        <div class="big-callout-text">El Servicio de Impuestos Internos (SII) interpuso una querella criminal contra los representantes de Ciudad Limpia S.A. por presunto uso y facilitación reiterada de <strong>facturas falsas</strong>, en el marco de una investigación a firmas del rubro del aseo.</div>
    </div>

    <div class="card-footer">
        <div>Fuente: Mercado Público / Diario Oficial / Servicio de Impuestos Internos</div>
        <div>ultimaprensa.cl</div>
    </div>
</div>
</body>
</html>""",

    "tarjeta_4_paradoja_vaciado": f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>{BASE_STYLE}</style>
</head>
<body>
<div class="card-wrapper">
    <div class="card-header">
        <div class="brand-badge"><span class="dot"></span> Última Prensa · Contrastes</div>
        <div class="category-pill">ANÁLISIS DE FACTIBILIDAD</div>
    </div>
    <div class="card-title">La Paradoja del Vaciado en Curaco (2026)</div>
    <div class="card-subtitle">Contraste entre el relato político regional del «terreno apto» y la geología intrínseca acreditada en tribunales.</div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 18px;">
        <div style="background: rgba(59, 130, 246, 0.06); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 12px; padding: 18px;">
            <div style="font-size: 11px; font-weight: 800; color: #60a5fa; letter-spacing: 1px; margin-bottom: 8px;">DISCURSO OFICIAL (JULIO 2026)</div>
            <div style="font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 8px;">Vaciado de 200.000 m³</div>
            <p style="font-size: 12px; color: #94a3b8; line-height: 1.5;">GORE Los Lagos (Alejandro Santana), Subdere y alcaldes afirman que desaguar el agua de lluvia del alvéolo demuestra que el terreno está «seco y apto» para un plan de <strong>US$31 millones</strong>.</p>
        </div>

        <div style="background: rgba(239, 68, 68, 0.06); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 18px;">
            <div style="font-size: 11px; font-weight: 800; color: #f87171; letter-spacing: 1px; margin-bottom: 8px;">VERDAD GEOLÓGICA Y JUDICIAL</div>
            <div style="font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 8px;">Falla Intrínseca del Suelo</div>
            <p style="font-size: 12px; color: #94a3b8; line-height: 1.5;">Sernageomin y Arcadis probaron que el agua no es solo lluvia: son <strong>afloramientos de napas subterráneas</strong>. El suelo alofánico pierde toda cohesión con la humedad. Las bombas mecánicas no cambian la física del suelo.</p>
        </div>
    </div>

    <div class="big-callout" style="background: rgba(234, 179, 8, 0.08); border-left-color: #eab308;">
        <div class="big-callout-title" style="color: #facc15;">RIESGO INMINENTE: CADUCIDAD AMBIENTAL (RCA)</div>
        <div class="big-callout-text">El proyecto enfrenta la causal de caducidad del <strong>Artículo 25 ter de la Ley N° 19.300</strong>, que extingue la Resolución de Calificación Ambiental si las obras materiales permanecen paralizadas por más de 5 años continuos (en Curaco van más de 10 años).</div>
    </div>

    <div class="card-footer">
        <div>Fuente: Sernageomin / Ley 19.300 / Dictámenes Corte Suprema</div>
        <div>ultimaprensa.cl</div>
    </div>
</div>
</body>
</html>"""
}


CARD_CONFIGS = {
    "tarjeta_1_alertas_geotecnicas": {"width": 860, "height": 840},
    "tarjeta_2_liquidacion_tribunales": {"width": 860, "height": 660},
    "tarjeta_3_megacontrato_mutacion": {"width": 860, "height": 700},
    "tarjeta_4_paradoja_vaciado": {"width": 860, "height": 660},
}


def render_cards(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "temp_html"
    temp_dir.mkdir(exist_ok=True)

    rendered_files = []

    for name, html_content in TEMPLATES.items():
        html_file = temp_dir / f"{name}.html"
        png_file = output_dir / f"{name}.png"
        cfg = CARD_CONFIGS.get(name, {"width": 860, "height": 680})
        
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Renderizando {name} a PNG Retina 2x ({cfg['width']}x{cfg['height']})...")
        cmd = [
            CHROME_BIN,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--force-device-scale-factor=2",
            f"--window-size={cfg['width']},{cfg['height']}",
            f"--screenshot={png_file}",
            f"file://{html_file.resolve()}"
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and png_file.exists():
            print(f"  ✓ {png_file.name} generado con éxito ({png_file.stat().st_size // 1024} KB)")
            rendered_files.append(png_file)
        else:
            print(f"  ✗ Error al renderizar {name}: {res.stderr}")

    return rendered_files


def generar_animaciones(png_files: list, output_dir: Path):
    """Genera animaciones de carrusel rotativo (GIF y WebP) a partir de las tarjetas PNG generadas."""
    if not png_files:
        return
    
    output_gif = output_dir / "carrusel_investigacion_curaco.gif"
    output_webp = output_dir / "carrusel_investigacion_curaco.webp"
    print(f"\nGenerando animaciones compuestas en: {output_dir}...")
    
    list_file = output_dir / "temp_html" / "images_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in png_files:
            f.write(f"file '{p.resolve()}'\nduration 4\n")
        f.write(f"file '{png_files[-1].resolve()}'\n")

    # 1. GIF optimizado (115 KB, compatible con emails y Substack)
    cmd_gif = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file.resolve()),
        "-vf", "fps=2,scale=760:720:force_original_aspect_ratio=decrease,pad=760:720:(ow-iw)/2:(oh-ih)/2:color=#090d16,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        str(output_gif.resolve())
    ]
    res_gif = subprocess.run(cmd_gif, capture_output=True, text=True)
    if res_gif.returncode == 0 and output_gif.exists():
        print(f"  ✓ GIF animado generado exitosamente: {output_gif.name} ({output_gif.stat().st_size // 1024} KB)")

    # 2. WebP animado (538 KB, alta fidelidad de color de 24 bits)
    cmd_webp = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file.resolve()),
        "-vf", "fps=2,scale=760:720:force_original_aspect_ratio=decrease,pad=760:720:(ow-iw)/2:(oh-ih)/2:color=#090d16",
        "-loop", "0", "-c:v", "libwebp", "-lossless", "0", "-q:v", "85",
        str(output_webp.resolve())
    ]
    res_webp = subprocess.run(cmd_webp, capture_output=True, text=True)
    if res_webp.returncode == 0 and output_webp.exists():
        print(f"  ✓ WebP animado generado exitosamente: {output_webp.name} ({output_webp.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    out_dir = Path("reportajes/caso_relleno_curaco_osorno/graficos")
    pngs = render_cards(out_dir)
    generar_animaciones(pngs, out_dir)
    print("\nProceso de generación gráfica completado.")
