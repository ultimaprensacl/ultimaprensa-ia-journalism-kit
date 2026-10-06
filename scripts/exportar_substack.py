"""
Conversor de Reportajes Markdown a HTML Estándar para Substack y CMS Digital
Última Prensa IA Journalism Kit
Soporta: Cintillos, H1/H2/H3, Blockquotes, Listas UL/OL, Tablas Markdown, Bloques de Código/Pre y Enlaces
"""

import os
import sys
import re
import html
import json
from pathlib import Path

# Cargar caché de uploads a Substack si existe
CDN_CACHE = {}
_cache_path = Path(__file__).resolve().parent.parent.parent / "reportajes" / "caso_relleno_curaco_osorno" / "graficos" / "substack_uploads_cache.json"
if _cache_path.exists():
    try:
        CDN_CACHE = json.loads(_cache_path.read_text(encoding="utf-8"))
    except Exception:
        pass


def md_to_substack_html(md_path: str, output_path: str):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    html_lines = []
    article_title = "Última Prensa — Publicación Digital"
    in_blockquote = False
    in_list = False
    list_type = None
    in_code_block = False
    code_block_lines = []
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        
        t_html = ['<div style="overflow-x: auto; margin: 24px 0;">',
                  '<table style="width: 100%; border-collapse: collapse; font-size: 15px; text-align: left; border: 1px solid #e2e8f0; font-family: inherit;">']
        
        is_first = True
        for row in table_rows:
            # Check if separator row
            if all(re.match(r'^:?-+:?$', c.strip()) for c in row if c.strip()):
                continue
            
            t_html.append('  <tr>')
            for cell in row:
                c_clean = cell.strip()
                c_clean = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', c_clean)
                c_clean = re.sub(r'\*(.*?)\*', r'<em>\1</em>', c_clean)
                c_clean = re.sub(r'`(.*?)`', r'<code style="background: #eee; padding: 2px 4px; border-radius: 3px; font-size: 13px;">\1</code>', c_clean)
                
                if is_first:
                    t_html.append(f'    <th style="background: #f8fafc; padding: 10px 14px; border: 1px solid #cbd5e1; font-weight: 700; color: #1e293b;">{c_clean}</th>')
                else:
                    t_html.append(f'    <td style="padding: 9px 14px; border: 1px solid #e2e8f0; color: #334155; vertical-align: top;">{c_clean}</td>')
            t_html.append('  </tr>')
            is_first = False
            
        t_html.append('</table></div>')
        html_lines.append("\n".join(t_html))
        table_rows = []
        in_table = False

    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.rstrip()

        # Handle Code Block fences
        if line.strip().startswith('```'):
            if in_table:
                flush_table()
            if in_blockquote:
                html_lines.append("</blockquote>")
                in_blockquote = False
            if in_list:
                html_lines.append(f"</{list_type}>")
                in_list = False
                list_type = None

            if in_code_block:
                # End of code block
                code_content = html.escape("\n".join(code_block_lines))
                html_lines.append(f'<pre style="background: #0f172a; color: #f8fafc; padding: 16px 20px; border-radius: 8px; font-size: 14px; line-height: 1.5; overflow-x: auto; margin: 24px 0;"><code>{code_content}</code></pre>')
                code_block_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_block_lines = []
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(raw_line.rstrip('\r\n'))
            i += 1
            continue

        # Handle Tables
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if in_blockquote:
                html_lines.append("</blockquote>")
                in_blockquote = False
            if in_list:
                html_lines.append(f"</{list_type}>")
                in_list = False
                list_type = None

            cells = [c for c in line.strip().split('|')[1:-1]]
            table_rows.append(cells)
            in_table = True
            i += 1
            continue
        elif in_table:
            flush_table()

        # Empty line
        if not line.strip():
            if in_blockquote:
                html_lines.append("</blockquote>")
                in_blockquote = False
            if in_list:
                html_lines.append(f"</{list_type}>")
                in_list = False
                list_type = None
            i += 1
            continue

        # Cintillo
        if line.startswith('[') and line.endswith(']'):
            cintillo_text = line[1:-1]
            html_lines.append(f'<p class="cintillo" style="font-weight: bold; letter-spacing: 1px; color: #d9381e; text-transform: uppercase; font-size: 13px; margin-bottom: 8px;">{html.escape(cintillo_text)}</p>')
            i += 1
            continue

        # H4 / Subsecciones
        if line.startswith('#### '):
            h4_text = line[5:].strip()
            h4_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', h4_text)
            h4_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', h4_text)
            html_lines.append(f'<h4 style="font-size: 18px; font-weight: 700; line-height: 1.35; margin-top: 24px; margin-bottom: 12px; color: #222;">{h4_text}</h4>')
            i += 1
            continue

        # H3 / Ladillos
        if line.startswith('### '):
            ladillo = line[4:].strip()
            html_lines.append(f'<h3 style="font-size: 22px; font-weight: 700; line-height: 1.3; margin-top: 36px; margin-bottom: 16px; color: #1a1a1a;">{html.escape(ladillo)}</h3>')
            i += 1
            continue

        # H2 / Bajada
        if line.startswith('## '):
            subhead = line[3:].strip()
            html_lines.append(f'<h2 style="font-size: 20px; font-weight: 400; line-height: 1.4; color: #444; margin-top: 0; margin-bottom: 24px;">{html.escape(subhead)}</h2>')
            i += 1
            continue

        # H1
        if line.startswith('# '):
            title = line[2:].strip()
            if article_title.startswith("Última Prensa"):
                article_title = f"{title} — Última Prensa"
            html_lines.append(f'<h1 style="font-size: 32px; font-weight: 800; line-height: 1.25; margin-bottom: 12px; color: #111;">{html.escape(title)}</h1>')
            i += 1
            continue

        # Separator hr
        if line.strip() == '---':
            if in_blockquote:
                html_lines.append("</blockquote>")
                in_blockquote = False
            if in_list:
                html_lines.append(f"</{list_type}>")
                in_list = False
                list_type = None
            html_lines.append('<hr style="border: 0; height: 1px; background: #e0e0e0; margin: 32px 0;">')
            i += 1
            continue

        # Blockquote
        if line.startswith('>'):
            if not in_blockquote:
                html_lines.append('<blockquote style="border-left: 4px solid #d9381e; background: #fdf8f7; padding: 14px 18px; margin: 20px 0; color: #2b2b2b; font-size: 16px; border-radius: 0 6px 6px 0;">')
                in_blockquote = True
            bq_content = line[1:].strip()
            if not bq_content:
                html_lines.append('<div style="height: 10px;"></div>')
                i += 1
                continue
            # formatting bold/italics
            bq_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', bq_content)
            bq_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', bq_content)
            bq_content = re.sub(r'`(.*?)`', r'<code style="background: #eee; padding: 2px 4px; border-radius: 3px; font-size: 14px;">\1</code>', bq_content)
            bq_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color: #d9381e; text-decoration: underline;">\1</a>', bq_content)
            if bq_content.startswith('- '):
                html_lines.append(f'<p style="margin: 4px 0 4px 16px; text-align: justify;">• {bq_content[2:]}</p>')
            else:
                html_lines.append(f'<p style="margin: 6px 0; text-align: justify;">{bq_content}</p>')
            i += 1
            continue
        elif in_blockquote:
            html_lines.append("</blockquote>")
            in_blockquote = False

        # Unordered list
        if line.startswith('- ') or line.startswith('* '):
            if not in_list or list_type != 'ul':
                if in_list:
                    html_lines.append(f"</{list_type}>")
                html_lines.append('<ul style="margin: 16px 0 20px 24px; padding-left: 0;">')
                in_list = True
                list_type = 'ul'
            item_text = line[2:].strip()
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
            item_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', item_text)
            item_text = re.sub(r'`(.*?)`', r'<code style="background: #eee; padding: 2px 4px; border-radius: 3px; font-size: 14px;">\1</code>', item_text)
            item_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color: #d9381e; text-decoration: underline;">\1</a>', item_text)
            html_lines.append(f'<li style="margin-bottom: 8px; text-align: justify;">{item_text}</li>')
            i += 1
            continue

        # Ordered list
        m_ol = re.match(r'^(\d+)\.\s+(.*)$', line)
        if m_ol:
            if not in_list or list_type != 'ol':
                if in_list:
                    html_lines.append(f"</{list_type}>")
                html_lines.append('<ol style="margin: 16px 0 20px 24px; padding-left: 0;">')
                in_list = True
                list_type = 'ol'
            item_text = m_ol.group(2).strip()
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
            item_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', item_text)
            item_text = re.sub(r'`(.*?)`', r'<code style="background: #eee; padding: 2px 4px; border-radius: 3px; font-size: 14px;">\1</code>', item_text)
            item_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color: #d9381e; text-decoration: underline;">\1</a>', item_text)
            html_lines.append(f'<li style="margin-bottom: 8px; text-align: justify;">{item_text}</li>')
            i += 1
            continue

        if in_list:
            html_lines.append(f"</{list_type}>")
            in_list = False
            list_type = None

        # Images and Figures
        m_img = re.match(r'^!\[(.*?)\]\((.*?)\)$', line.strip())
        if m_img:
            if in_blockquote:
                html_lines.append("</blockquote>")
                in_blockquote = False
            if in_list:
                html_lines.append(f"</{list_type}>")
                in_list = False
                list_type = None

            alt_text = m_img.group(1).strip()
            img_src = m_img.group(2).strip()
            fname = Path(img_src).name
            display_src = CDN_CACHE[fname]["url"] if fname in CDN_CACHE else img_src

            # Check if next line is caption
            caption_text = ""
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('*') and next_line.endswith('*') and not next_line.startswith('**'):
                    caption_text = next_line[1:-1].strip()
                    caption_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', caption_text)
                    i += 1  # consume caption line

            is_gif = img_src.lower().endswith('.gif')
            is_carrusel = 'carrusel' in img_src.lower()
            is_evidencia = 'evidencia' in img_src.lower()
            is_diagrama = 'diagrama' in img_src.lower()

            if is_carrusel:
                badge_title = "Rotación Continua (4 Ejes)"
            elif is_gif:
                badge_title = "Animación Minimalista Mate"
            elif is_evidencia:
                badge_title = "Dossier Forense Oficial"
            elif is_diagrama:
                badge_title = "Diagrama de Malla Financiera"
            else:
                badge_title = "Infografía Editorial"

            header_extra = f"""    <div style="display: flex; align-items: center; justify-content: space-between; padding: 6px 12px 10px 12px; border-bottom: 1px solid #f1f5f9; margin-bottom: 8px;">
      <span style="font-size: 11px; font-weight: 800; color: #d9381e; text-transform: uppercase; letter-spacing: 1.5px; display: inline-flex; align-items: center; gap: 6px;">
        <span style="width: 8px; height: 8px; background: #d9381e; border-radius: 50%; display: inline-block;"></span>
        Infografía Dinámica • Última Prensa
      </span>
      <span style="font-size: 11px; color: #64748b; font-weight: 600;">{badge_title}</span>
    </div>\n"""

            card_bg = "#ffffff"
            border_color = "#e2e8f0"
            shadow = "0 8px 24px rgba(0, 0, 0, 0.04)"
            loading_attr = "eager" if is_gif else "lazy"

            fig_html = f"""<figure style="margin: 32px 0; text-align: center;">
  <div style="background: {card_bg}; border-radius: 12px; padding: 10px; border: 1px solid {border_color}; box-shadow: {shadow}; overflow: hidden; display: inline-block; max-width: 100%;">
{header_extra}    <img src="{display_src}" alt="{html.escape(alt_text)}" style="max-width: 100%; height: auto; border-radius: 8px; display: block;" loading="{loading_attr}">
  </div>"""
            if caption_text:
                fig_html += f"""
  <figcaption style="font-size: 13.5px; color: #64748b; line-height: 1.5; margin-top: 10px; font-style: italic; text-align: center;">
    {caption_text}
  </figcaption>"""
            fig_html += "\n</figure>"
            html_lines.append(fig_html)
            i += 1
            continue

        # Normal Paragraph
        p_text = line.strip()
        p_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p_text)
        p_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', p_text)
        p_text = re.sub(r'`(.*?)`', r'<code style="background: #eee; padding: 2px 4px; border-radius: 3px; font-size: 14px;">\1</code>', p_text)
        p_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color: #d9381e; text-decoration: underline;">\1</a>', p_text)
        
        # Byline style check
        if p_text.startswith('<strong>Por '):
            html_lines.append(f'<p style="font-size: 15px; color: #555; margin-bottom: 20px; font-style: italic;">{p_text}</p>')
        else:
            html_lines.append(f'<p style="font-size: 17px; line-height: 1.65; color: #222; margin-bottom: 18px; text-align: justify;">{p_text}</p>')
        i += 1

    if in_table:
        flush_table()
    if in_blockquote:
        html_lines.append("</blockquote>")
    if in_list:
        html_lines.append(f"</{list_type}>")
    if in_code_block:
        code_content = html.escape("\n".join(code_block_lines))
        html_lines.append(f'<pre style="background: #0f172a; color: #f8fafc; padding: 16px 20px; border-radius: 8px; font-size: 14px; line-height: 1.5; overflow-x: auto; margin: 24px 0;"><code>{code_content}</code></pre>')

    body_html = "\n".join(html_lines)

    complete_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(article_title)}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 760px; margin: 40px auto; padding: 0 20px; background: #ffffff;">

<!-- CONTENIDO COPIABLE DIRECTAMENTE PARA SUBSTACK -->
<div class="substack-post-body">
{body_html}
</div>

</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(complete_html)

    print(f"Reportaje exportado a HTML exitosamente en: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python scripts/exportar_substack.py <archivo.md> [archivo_salida.html]")
        sys.exit(1)
    
    md_in = sys.argv[1]
    html_out = sys.argv[2] if len(sys.argv) > 2 else str(Path(md_in).with_suffix(".html"))
    md_to_substack_html(md_in, html_out)
