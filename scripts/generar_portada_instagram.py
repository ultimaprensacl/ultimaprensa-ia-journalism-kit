#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_portada_instagram.py — Generador de Portadas 4K para Instagram de Última Prensa
Recrea fielmente el formato editorial canónico de Última Prensa para el feed de Instagram (Portrait 4:5):
  - Badge superior de marca con logo transparente y tipografía serif.
  - Foto de portada con tratamiento B&W cálido de alto contraste y fade-to-black.
  - Sello / estampilla editorial inclinada con borde terracota y tracking expandido.
  - Titular en Newsreader/Playfair Display con resaltado en cursiva terracota/coral.
  - Metadatos con barra de acento y tipografía técnica.
  - Pie con suscripción a Substack y cuenta de Instagram.

Renderizado a resolución nativa 4K (2160 × 2700 px) mediante Chromium Headless.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
DEFAULT_LOGO = BASE_DIR / "assets" / "brand" / "logo_typewriter_transparente.png"
CHROMIUM_BIN = "/usr/bin/chromium"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;0,6..72,700;1,6..72,400;1,6..72,600&family=Playfair+Display:ital,wght@0,600;0,700;0,900;1,600;1,700&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    width: {width}px;
    height: {height}px;
    background-color: #141312;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #f8f7f5;
    position: relative;
    overflow: hidden;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
}}

/* Contenedor Fotográfico Superior */
.photo-container {{
    position: absolute;
    top: 0;
    left: 0;
    width: {width}px;
    height: {photo_height}px;
    overflow: hidden;
}}

.photo-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center {photo_v_pos};
    filter: {photo_filter};
    transform: scale(1.02);
}}

/* Capa de calidez tonal armónica con el logo */
.warm-tint {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at 50% 30%, rgba(217, 78, 52, 0.05) 0%, rgba(18, 17, 16, 0.25) 70%, rgba(18, 17, 16, 0.6) 100%);
    mix-blend-mode: multiply;
    pointer-events: none;
}}

/* Degradado progresivo hacia el fondo oscuro */
.photo-gradient {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        180deg,
        rgba(20, 19, 18, 0.0) 0%,
        rgba(20, 19, 18, 0.0) 35%,
        rgba(20, 19, 18, 0.4) 55%,
        rgba(20, 19, 18, 0.85) 75%,
        rgba(20, 19, 18, 0.98) 90%,
        #141312 100%
    );
    pointer-events: none;
}}

/* Badge Superior de Marca (Logo + Nombre) */
.brand-badge {{
    position: absolute;
    top: {badge_top}px;
    left: {padding_x}px;
    display: inline-flex;
    align-items: center;
    gap: {badge_gap}px;
    background-color: #faf7f0;
    padding: {badge_pad_y}px {badge_pad_x}px;
    border-radius: {badge_radius}px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45), 0 2px 8px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    z-index: 10;
}}

.brand-logo-img {{
    width: {logo_size}px;
    height: {logo_size}px;
    object-fit: contain;
}}

.brand-name {{
    font-family: 'Newsreader', 'Playfair Display', Georgia, serif;
    font-size: {brand_font_size}px;
    font-weight: 700;
    color: #1a1918;
    letter-spacing: -0.5px;
}}

/* Sello / Estampilla Editorial Inclinada */
.editorial-stamp {{
    position: absolute;
    top: {stamp_top}px;
    left: {padding_x}px;
    transform: rotate({stamp_rotate}deg);
    background-color: #ffffff;
    border: {stamp_border_w}px solid #d94e34;
    padding: {stamp_pad_y}px {stamp_pad_x}px;
    border-radius: {stamp_radius}px;
    box-shadow: 0 16px 45px rgba(0, 0, 0, 0.55), 0 4px 12px rgba(217, 78, 52, 0.2);
    display: inline-block;
    z-index: 15;
}}

.stamp-text {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: {stamp_font_size}px;
    font-weight: 800;
    color: #d94e34;
    letter-spacing: {stamp_tracking}px;
    text-transform: uppercase;
    display: block;
}}

/* Bloque Inferior de Contenido */
.editorial-bottom {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: {width}px;
    padding: 0 {padding_x}px {padding_bottom}px {padding_x}px;
    z-index: 20;
    display: flex;
    flex-direction: column;
}}

/* Titular Principal */
.headline {{
    font-family: 'Newsreader', 'Playfair Display', Georgia, serif;
    font-size: {headline_size}px;
    line-height: {headline_line_height};
    font-weight: 400;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin-bottom: {headline_margin_b}px;
    text-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
}}

.headline .destacado {{
    color: #df5844;
    font-style: italic;
    font-weight: 600;
}}

/* Cintillo de Categoría y Localidad */
.meta-row {{
    display: flex;
    align-items: center;
    gap: {meta_gap}px;
    margin-bottom: {meta_margin_b}px;
}}

.meta-accent {{
    width: {accent_w}px;
    height: {accent_h}px;
    background-color: #df5844;
    border-radius: 2px;
}}

.meta-tags {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: {meta_font_size}px;
    font-weight: 700;
    letter-spacing: {meta_tracking}px;
    color: #a39e97;
    text-transform: uppercase;
}}

/* Línea sutil de separación */
.footer-divider {{
    width: 100%;
    height: 1px;
    background-color: rgba(255, 255, 255, 0.1);
    margin-bottom: {footer_margin_t}px;
}}

/* Pie de Suscripción e Instagram */
.footer-row {{
    display: flex;
    flex-direction: column;
    gap: {footer_gap}px;
}}

.footer-line {{
    font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace;
    font-size: {footer_font_size}px;
    font-weight: 500;
    color: #8c867e;
    letter-spacing: 0.3px;
}}

.footer-line .hl-coral {{
    color: #df5844;
    font-weight: 600;
}}

.footer-line .hl-white {{
    color: #ffffff;
    font-weight: 600;
}}
</style>
</head>
<body>

<div class="photo-container">
    <img src="{photo_url}" class="photo-img" alt="Portada">
    <div class="warm-tint"></div>
    <div class="photo-gradient"></div>
</div>

<div class="brand-badge">
    <img src="{logo_url}" class="brand-logo-img" alt="Logo Última Prensa">
    <span class="brand-name">Última Prensa</span>
</div>

{stamp_html}

<div class="editorial-bottom">
    <div class="headline">
        {formatted_headline}
    </div>

    <div class="meta-row">
        <div class="meta-accent"></div>
        <div class="meta-tags">{tags_text}</div>
    </div>

    <div class="footer-divider"></div>

    <div class="footer-row">
        <div class="footer-line">
            Suscríbete gratis en <span class="hl-coral">ultimaprensacl.substack.com</span>
        </div>
        <div class="footer-line">
            Síguenos en Instagram <span class="hl-white">@ultimaprensa.cl</span>
        </div>
    </div>
</div>

</body>
</html>
"""

def formatear_titular(titular: str, destacados: list) -> str:
    """Resalta en cursiva coral las palabras o frases clave en el titular."""
    resultado = titular.strip()
    for d in destacados:
        d = d.strip()
        if not d:
            continue
        # Reemplaza respetando mayúsculas/minúsculas exactas
        if d in resultado:
            resultado = resultado.replace(d, f'<span class="destacado">{d}</span>')
        else:
            # Búsqueda insensible a mayúsculas
            import re
            pattern = re.compile(re.escape(d), re.IGNORECASE)
            match = pattern.search(resultado)
            if match:
                original = match.group(0)
                resultado = resultado.replace(original, f'<span class="destacado">{original}</span>')
    return resultado

def generar_portada(
    imagen_path: str,
    titular: str,
    sticker: str = "CASO OSORNO",
    tags: str = "INVESTIGACIÓN · OSORNO · LOS LAGOS",
    destacados: list = None,
    filtro: str = "byn-calido",
    resolucion: str = "4k",
    out_path: str = None,
    logo_path: str = None,
    photo_v_pos: str = "25%"
):
    if destacados is None:
        destacados = []

    p_img = Path(imagen_path).resolve()
    if not p_img.exists():
        raise FileNotFoundError(f"No existe la imagen: {imagen_path}")

    p_logo = Path(logo_path).resolve() if logo_path else DEFAULT_LOGO.resolve()
    if not p_logo.exists():
        # Fallback si no está el transparente
        p_logo = p_img

    if out_path:
        p_out = Path(out_path).resolve()
    else:
        p_out = SCRIPT_DIR.parent / "portada_instagram_4k.png"

    p_out.parent.mkdir(parents=True, exist_ok=True)

    # Parámetros según resolución
    if resolucion.lower() == "4k":
        w, h = 2160, 2700
        scale = 2.0
    else:
        w, h = 1080, 1350
        scale = 1.0

    # Ajuste dinámico del tamaño de fuente del titular según extensión
    # Un titular largo (> 120 caracteres) debe tener una fuente ligeramente menor
    longitud = len(titular)
    if longitud > 160:
        headline_size = int(68 * scale)
        headline_lh = 1.18
        stamp_top = int(600 * scale)
        photo_h = int(820 * scale)
    elif longitud > 120:
        headline_size = int(74 * scale)
        headline_lh = 1.18
        stamp_top = int(630 * scale)
        photo_h = int(850 * scale)
    elif longitud > 80:
        headline_size = int(82 * scale)
        headline_lh = 1.18
        stamp_top = int(670 * scale)
        photo_h = int(890 * scale)
    else:
        headline_size = int(92 * scale)
        headline_lh = 1.16
        stamp_top = int(720 * scale)
        photo_h = int(930 * scale)

    # Filtros fotográficos
    if filtro == "byn-calido":
        photo_filter = "grayscale(100%) sepia(20%) contrast(125%) brightness(95%)"
    elif filtro == "byn":
        photo_filter = "grayscale(100%) contrast(120%) brightness(95%)"
    elif filtro == "desaturado":
        photo_filter = "saturate(0.4) contrast(115%) brightness(95%)"
    else:
        photo_filter = "none"

    formatted_headline = formatear_titular(titular, destacados)

    # Estampilla / Sello editorial (opcional)
    if sticker and sticker.strip():
        stamp_html = f"""<div class="editorial-stamp">
    <span class="stamp-text">{sticker.strip()}</span>
</div>"""
    else:
        stamp_html = ""

    # Variables CSS escaladas
    params = {
        "width": w,
        "height": h,
        "photo_height": photo_h,
        "photo_url": p_img.as_uri(),
        "logo_url": p_logo.as_uri(),
        "photo_v_pos": photo_v_pos,
        "photo_filter": photo_filter,
        "badge_top": int(60 * scale),
        "padding_x": int(60 * scale),
        "badge_gap": int(16 * scale),
        "badge_pad_y": int(14 * scale),
        "badge_pad_x": int(26 * scale),
        "badge_radius": int(8 * scale),
        "logo_size": int(46 * scale),
        "brand_font_size": int(28 * scale),
        "stamp_top": stamp_top,
        "stamp_rotate": -4,
        "stamp_border_w": int(3.5 * scale),
        "stamp_pad_y": int(12 * scale),
        "stamp_pad_x": int(32 * scale),
        "stamp_radius": int(4 * scale),
        "stamp_font_size": int(34 * scale),
        "stamp_tracking": int(5 * scale),
        "stamp_html": stamp_html,
        "padding_bottom": int(60 * scale),
        "headline_size": headline_size,
        "headline_line_height": headline_lh,
        "headline_margin_b": int(32 * scale),
        "formatted_headline": formatted_headline,
        "meta_gap": int(16 * scale),
        "meta_margin_b": int(28 * scale),
        "accent_w": int(36 * scale),
        "accent_h": int(4 * scale),
        "meta_font_size": int(18 * scale),
        "meta_tracking": int(3.5 * scale),
        "tags_text": tags,
        "footer_margin_t": int(24 * scale),
        "footer_gap": int(8 * scale),
        "footer_font_size": int(16 * scale),
    }

    html_content = HTML_TEMPLATE.format(**params)
    temp_html = p_out.parent / f"temp_{p_out.stem}.html"
    temp_html.write_text(html_content, encoding="utf-8")

    print(f"[*] Renderizando portada con Chromium a {w}x{h} ({resolucion.upper()})...")
    cmd = [
        CHROMIUM_BIN,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--screenshot={p_out.resolve()}",
        f"--window-size={w},{h}",
        f"file://{temp_html.resolve()}"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Fallo en Chromium: {res.stderr}")

    print(f"[+] Portada 4K generada exitosamente en: {p_out}")

    # Generamos versión JPG optimizada para feed directo (máximo 8MB en IG)
    p_jpg = p_out.with_suffix(".jpg")
    try:
        im = Image.open(p_out).convert("RGB")
        im.save(p_jpg, "JPEG", quality=95, optimize=True)
        print(f"[+] Versión JPG para Instagram generada en: {p_jpg}")
    except Exception as e:
        print(f"[!] Aviso al generar JPG: {e}")

    # Limpiamos temp si no se solicita depuración
    if temp_html.exists():
        temp_html.unlink()

    return p_out

def main():
    parser = argparse.ArgumentParser(description="Generador de Portadas 4K para Instagram de Última Prensa")
    parser.add_argument("--imagen", "-i", required=True, help="Ruta a la fotografía de fondo")
    parser.add_argument("--titular", "-t", required=True, help="Titular principal del reportaje")
    parser.add_argument("--sticker", "-s", default="CASO OSORNO", help="Texto del sello inclinado")
    parser.add_argument("--sin-sticker", action="store_true", help="Omitir el sello/letrero inclinado")
    parser.add_argument("--tags", default="INVESTIGACIÓN · OSORNO · LOS LAGOS", help="Cintillo de categoría y región")
    parser.add_argument("--destacado", "-d", default="sin orden judicial, alta peligrosidad", help="Frases a resaltar en cursiva coral")
    parser.add_argument("--filtro", default="byn-calido", choices=["byn-calido", "byn", "desaturado", "color"], help="Tratamiento fotográfico")
    parser.add_argument("--resolucion", default="4k", choices=["4k", "standard"], help="Resolución de salida")
    parser.add_argument("--logo", help="Ruta alternativa al logo")
    parser.add_argument("--vpos", default="25%", help="Alineación vertical de la foto (e.g. 25%%, top, center)")
    parser.add_argument("--out", "-o", help="Ruta de destino del archivo PNG")

    args = parser.parse_args()
    destacados = [d.strip() for d in args.destacado.split(",") if d.strip()]
    sticker_final = "" if args.sin_sticker else args.sticker

    generar_portada(
        imagen_path=args.imagen,
        titular=args.titular,
        sticker=sticker_final,
        tags=args.tags,
        destacados=destacados,
        filtro=args.filtro,
        resolucion=args.resolucion,
        out_path=args.out,
        logo_path=args.logo,
        photo_v_pos=args.vpos
    )

if __name__ == "__main__":
    main()
