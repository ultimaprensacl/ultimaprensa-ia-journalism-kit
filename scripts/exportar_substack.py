"""
Conversor de Reportajes Markdown a HTML Estándar para Substack y CMS Digital
Última Prensa IA Journalism Kit
"""

import os
import sys
import re
import html


def md_to_substack_html(md_path: str, output_path: str):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    html_lines = []
    article_title = "Última Prensa — Publicación Digital"
    in_blockquote = False
    in_list = False
    list_type = None

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
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

        # H1
        if line.startswith('# '):
            title = line[2:].strip()
            if article_title.startswith("Última Prensa"):
                article_title = f"{title} — Última Prensa"
            html_lines.append(f'<h1 style="font-size: 32px; font-weight: 800; line-height: 1.25; margin-bottom: 12px; color: #111;">{html.escape(title)}</h1>')
            i += 1
            continue


        # H2 / Bajada
        if line.startswith('## '):
            subhead = line[3:].strip()
            html_lines.append(f'<h2 style="font-size: 20px; font-weight: 400; line-height: 1.4; color: #444; margin-top: 0; margin-bottom: 24px;">{html.escape(subhead)}</h2>')
            i += 1
            continue

        # H3 / Ladillos
        if line.startswith('### '):
            ladillo = line[4:].strip()
            html_lines.append(f'<h3 style="font-size: 22px; font-weight: 700; line-height: 1.3; margin-top: 36px; margin-bottom: 16px; color: #1a1a1a;">{html.escape(ladillo)}</h3>')
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
            html_lines.append('<hr style="border: 0; height: 1px; background: #e0e0e0; margin: 32px 0;">')
            i += 1
            continue

        # Blockquote
        if line.startswith('> '):
            if not in_blockquote:
                html_lines.append('<blockquote style="border-left: 4px solid #d9381e; background: #fdf8f7; padding: 14px 18px; margin: 20px 0; color: #2b2b2b; font-size: 16px; border-radius: 0 6px 6px 0;">')
                in_blockquote = True
            bq_line = line[2:].strip()
            # formatting bold/italics
            bq_line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', bq_line)
            bq_line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', bq_line)
            bq_line = re.sub(r'`(.*?)`', r'<code style="background: #eee; padding: 2px 4px; border-radius: 3px; font-size: 14px;">\1</code>', bq_line)
            if bq_line.startswith('- '):
                html_lines.append(f'<p style="margin: 4px 0 4px 16px;">• {bq_line[2:]}</p>')
            else:
                html_lines.append(f'<p style="margin: 6px 0;">{bq_line}</p>')
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
            html_lines.append(f'<li style="margin-bottom: 8px;">{item_text}</li>')
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
            html_lines.append(f'<li style="margin-bottom: 8px;">{item_text}</li>')
            i += 1
            continue

        if in_list:
            html_lines.append(f"</{list_type}>")
            in_list = False
            list_type = None

        # Normal Paragraph
        p_text = line.strip()
        p_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p_text)
        p_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', p_text)
        p_text = re.sub(r'`(.*?)`', r'<code style="background: #eee; padding: 2px 4px; border-radius: 3px; font-size: 14px;">\1</code>', p_text)
        
        # Byline style check
        if p_text.startswith('<strong>Por '):
            html_lines.append(f'<p style="font-size: 15px; color: #555; margin-bottom: 20px; font-style: italic;">{p_text}</p>')
        else:
            html_lines.append(f'<p style="font-size: 17px; line-height: 1.65; color: #222; margin-bottom: 18px;">{p_text}</p>')
        i += 1

    if in_blockquote:
        html_lines.append("</blockquote>")
    if in_list:
        html_lines.append(f"</{list_type}>")

    body_html = "\n".join(html_lines)

    complete_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(article_title)}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; background: #ffffff;">

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
    default_md = '/home/pablo/Escritorio/Ultimaprensa/reportajes/caso_ip_los_lagos/reportaje_final.md'
    default_html = '/home/pablo/Escritorio/Ultimaprensa/reportajes/caso_ip_los_lagos/reportaje_substack.html'
    
    md_in = sys.argv[1] if len(sys.argv) > 1 else default_md
    html_out = sys.argv[2] if len(sys.argv) > 2 else default_html
    md_to_substack_html(md_in, html_out)

