#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publicar_substack_n8n.py — Cliente de Publicación Automatizada a Substack para Última Prensa.

Soporta dos modalidades:
  1. Vía webhook de n8n (http://localhost:5678/webhook/publicar-borrador-substack)
  2. Vía directa a la API de Substack (usando la cookie substack.sid)

Uso:
  python kit-journalism/scripts/publicar_substack_n8n.py \
      --archivo reportajes/caso_terminal_buses_osorno/reportaje_substack.html \
      --titulo "El negocio millonario de la concesión del Terminal de Buses de Osorno" \
      --bajada "Crónica de un canon congelado y 30 años sin licitación competitiva" \
      --modo n8n
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# Cargar variables desde n8n/.env si existen
def cargar_env_local():
    env_file = Path(__file__).resolve().parent.parent.parent / "n8n" / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("\"'")
                    if k not in os.environ:
                        os.environ[k] = v

cargar_env_local()

SUBSTACK_SID = os.environ.get("SUBSTACK_SID", "")
SUBSTACK_SUBDOMAIN = os.environ.get("SUBSTACK_SUBDOMAIN", "ultimaprensacl")
SUBSTACK_USER_ID = os.environ.get("SUBSTACK_USER_ID", "488459781")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/publicar-borrador-substack")

def extraer_metadatos_archivo(ruta_archivo: Path):
    """Extrae título, subtítulo y contenido del archivo HTML o Markdown."""
    contenido = ruta_archivo.read_text(encoding="utf-8")
    titulo = ""
    subtitulo = ""
    html = contenido

    if ruta_archivo.suffix.lower() == ".html":
        # Intentar extraer h1 o title
        import re
        m_title = re.search(r"<title>(.*?)</title>", contenido, re.IGNORECASE)
        if m_title:
            titulo = m_title.group(1).strip()
        m_h1 = re.search(r"<h1[^>]*>(.*?)</h1>", contenido, re.IGNORECASE)
        if m_h1 and not titulo:
            titulo = re.sub(r"<[^>]+>", "", m_h1.group(1)).strip()
        m_p = re.search(r"<p[^>]*class=[\"']lead[\"'][^>]*>(.*?)</p>", contenido, re.IGNORECASE)
        if m_p:
            subtitulo = re.sub(r"<[^>]+>", "", m_p.group(1)).strip()
    elif ruta_archivo.suffix.lower() == ".md":
        # Si es markdown, buscar primer h1 y compilar a html básico
        lines = contenido.splitlines()
        body_lines = []
        for line in lines:
            if line.startswith("# ") and not titulo:
                titulo = line[2:].strip()
            elif line.startswith("## ") and not subtitulo:
                subtitulo = line[3:].strip()
            else:
                body_lines.append(line)
        # Importar markdown si está disponible
        try:
            import markdown
            html = markdown.markdown("\n".join(body_lines))
        except ImportError:
            html = "\n".join(body_lines)

    return titulo, subtitulo, html

def enviar_a_n8n(titulo: str, subtitulo: str, html: str, token: str, publicacion: str, webhook_url: str):
    """Envía el contenido al webhook de n8n."""
    payload = {
        "title": titulo,
        "subtitle": subtitulo,
        "html": html,
        "token": token,
        "publication": publicacion
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "UltimaPrensa-CLI/1.0"
        },
        method="POST"
    )

    print(f"[*] Enviando payload a n8n ({webhook_url})...")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            res_json = json.loads(raw)
            print("[+] ¡Respuesta exitosa de n8n!")
            print(json.dumps(res_json, indent=2, ensure_ascii=False))
            return res_json
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        print(f"[-] Error HTTP de n8n ({e.code}): {err_msg}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[-] Error de conexión con n8n: {e}", file=sys.stderr)
        return None

def parsear_html_a_prosemirror(html_text: str, titulo_articulo: str = "", subtitulo_articulo: str = ""):
    """Convierte texto HTML a un documento ProseMirror de Substack con párrafos justificados y orden editorial estricto."""
    import re

    def strip_tags(s):
        s = re.sub(r"<[^>]*>", "", s)
        s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
        return s

    def parse_inline(text):
        nodes = []
        rem = text
        while rem:
            m_link = re.match(r"^<a\s+href=[\"']([^\"']*)[\"'][^>]*>([\s\S]*?)</a>", rem, re.IGNORECASE)
            m_bold = re.match(r"^<(strong|b)>([\s\S]*?)</(strong|b)>", rem, re.IGNORECASE)
            m_em = re.match(r"^<(em|i)>([\s\S]*?)</(em|i)>", rem, re.IGNORECASE)
            m_code = re.match(r"^<code[^>]*>([\s\S]*?)</code>", rem, re.IGNORECASE)
            m_tag = re.match(r"^<[^>]+>", rem)
            if m_link:
                nodes.append({"type": "text", "text": strip_tags(m_link.group(2)), "marks": [{"type": "link", "attrs": {"href": m_link.group(1)}}]})
                rem = rem[len(m_link.group(0)):]
            elif m_bold:
                nodes.append({"type": "text", "text": strip_tags(m_bold.group(2)), "marks": [{"type": "bold"}]})
                rem = rem[len(m_bold.group(0)):]
            elif m_em:
                nodes.append({"type": "text", "text": strip_tags(m_em.group(2)), "marks": [{"type": "italic"}]})
                rem = rem[len(m_em.group(0)):]
            elif m_code:
                nodes.append({"type": "text", "text": strip_tags(m_code.group(1)), "marks": [{"type": "code"}]})
                rem = rem[len(m_code.group(0)):]
            elif m_tag and rem.startswith(m_tag.group(0)):
                rem = rem[len(m_tag.group(0)):]
            else:
                next_tag = rem.find("<")
                chunk = rem[:next_tag] if next_tag != -1 else rem
                cleaned = strip_tags(chunk)
                if cleaned:
                    nodes.append({"type": "text", "text": cleaned})
                rem = rem[next_tag:] if next_tag != -1 else ""
        return nodes if nodes else [{"type": "text", "text": " "}]

    # Extraer cuerpo interior
    body_match = re.search(r"<body[^>]*>([\s\S]*)</body>", html_text, re.IGNORECASE)
    inner = body_match.group(1) if body_match else html_text

    # Eliminar bloques repetitivos de cabecera si están en el cuerpo
    inner = re.sub(r"<header[^>]*>[\s\S]*?</header>", "", inner, flags=re.IGNORECASE)
    inner = re.sub(r"<h1[^>]*>[\s\S]*?</h1>", "", inner, count=1, flags=re.IGNORECASE)
    inner = re.sub(r"<h2[^>]*>[\s\S]*?</h2>", "", inner, count=1, flags=re.IGNORECASE)
    inner = re.sub(r"<p[^>]*>\s*<strong>\s*Por Equipo de Investigación[^<]*</strong>\s*</p>", "", inner, count=1, flags=re.IGNORECASE)

    raw_blocks = []
    parts = re.split(r"(?=<(?:h[1-6]|p|hr|blockquote|ul|ol)[ >/])", inner, flags=re.IGNORECASE)
    for part in parts:
        s = part.strip()
        if not s:
            continue
        # Encabezados
        m_h = re.match(r"^<h(\d)[^>]*>(.*?)</h\1>", s, re.DOTALL | re.IGNORECASE)
        if m_h:
            lvl = int(m_h.group(1))
            # Ajustar jerarquía: h1 y h2 mapean a 2, h3 a 3
            target_lvl = 2 if lvl <= 2 else (3 if lvl == 3 else 4)
            raw_blocks.append({"type": "heading", "attrs": {"level": target_lvl}, "content": parse_inline(m_h.group(2))})
            continue

        # Regla horizontal divisoria
        if re.match(r"^<hr", s, re.IGNORECASE):
            raw_blocks.append({"type": "horizontal_rule"})
            continue

        # Bloques de cita (blockquote)
        m_bq = re.match(r"^<blockquote[^>]*>([\s\S]*?)</blockquote>", s, re.IGNORECASE)
        if m_bq:
            sub_p = re.findall(r"<p[^>]*>([\s\S]*?)</p>", m_bq.group(1), re.IGNORECASE)
            bq_children = []
            if sub_p:
                for sp in sub_p:
                    text_sp = strip_tags(sp).strip()
                    if text_sp.startswith("•"):
                        bq_children.append({
                            "type": "paragraph",
                            "attrs": {"textAlign": "justify"},
                            "content": parse_inline(re.sub(r"^[•\s]+", "", sp))
                        })
                    else:
                        bq_children.append({
                            "type": "paragraph",
                            "attrs": {"textAlign": "justify"},
                            "content": parse_inline(sp)
                        })
            else:
                bq_children.append({
                    "type": "paragraph",
                    "attrs": {"textAlign": "justify"},
                    "content": parse_inline(m_bq.group(1))
                })
            raw_blocks.append({"type": "blockquote", "content": bq_children})
            continue

        # Párrafos y viñetas
        m_p = re.match(r"^<p[^>]*>(.*?)</p>", s, re.DOTALL | re.IGNORECASE)
        if m_p:
            raw_text = strip_tags(m_p.group(1)).strip()
            if not raw_text:
                continue
            # Detección de viñetas
            if raw_text.startswith("•"):
                clean_item = re.sub(r"^[•\s]+", "", m_p.group(1))
                raw_blocks.append({
                    "type": "bullet_list",
                    "content": [{
                        "type": "list_item",
                        "content": [{
                            "type": "paragraph",
                            "attrs": {"textAlign": "justify"},
                            "content": parse_inline(clean_item)
                        }]
                    }]
                })
                continue

            # Párrafo normal siempre justificado
            raw_blocks.append({
                "type": "paragraph",
                "attrs": {"textAlign": "justify"},
                "content": parse_inline(m_p.group(1))
            })
            continue

        # Texto suelto residual
        cleaned = strip_tags(s).strip()
        if cleaned:
            raw_blocks.append({
                "type": "paragraph",
                "attrs": {"textAlign": "justify"},
                "content": [{"type": "text", "text": cleaned}]
            })

    # Fusionar listas adyacentes del mismo tipo para orden y limpieza
    merged_blocks = []
    for b in raw_blocks:
        if b.get("type") == "bullet_list" and merged_blocks and merged_blocks[-1].get("type") == "bullet_list":
            merged_blocks[-1]["content"].extend(b["content"])
        elif b.get("type") == "ordered_list" and merged_blocks and merged_blocks[-1].get("type") == "ordered_list":
            merged_blocks[-1]["content"].extend(b["content"])
        else:
            merged_blocks.append(b)

    return {"type": "doc", "attrs": {"schemaVersion": "v1"}, "content": merged_blocks}

def enviar_directo_substack(titulo: str, subtitulo: str, html: str, token: str, publicacion: str, user_id: str = SUBSTACK_USER_ID, draft_id: int = None):
    """Envía o actualiza el borrador directamente a la API de Substack con formato justificado."""
    if not token:
        print("[-] Error: No se proporcionó la cookie substack.sid (SUBSTACK_SID).", file=sys.stderr)
        return None

    prosemirror_doc = parsear_html_a_prosemirror(html, titulo_articulo=titulo, subtitulo_articulo=subtitulo)
    payload = {
        "draft_title": titulo,
        "draft_subtitle": subtitulo,
        "draft_body": json.dumps(prosemirror_doc),
        "draft_section_id": None,
        "draft_bylines": [{"id": int(user_id), "is_guest": False}],
        "audience": "everyone",
        "type": "newsletter"
    }
    data_bytes = json.dumps(payload).encode("utf-8")

    if draft_id:
        url = f"https://{publicacion}.substack.com/api/v1/drafts/{draft_id}"
        metodo = "PUT"
        print(f"[*] Actualizando borrador existente {draft_id} en Substack ({url})...")
    else:
        url = f"https://{publicacion}.substack.com/api/v1/drafts"
        metodo = "POST"
        print(f"[*] Creando nuevo borrador justificado en Substack ({url})...")

    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "Cookie": f"substack.sid={token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Origin": f"https://{publicacion}.substack.com",
            "Referer": f"https://{publicacion}.substack.com/publish"
        },
        method=metodo
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            res_json = json.loads(raw)
            d_id = res_json.get("id", draft_id)
            print("[+] ¡Borrador justificado y ordenado exitosamente en Substack!")
            print(f"    - ID del borrador: {d_id}")
            print(f"    - Título: {res_json.get('draft_title', titulo)}")
            print(f"    - Enlace para editar y publicar: https://{publicacion}.substack.com/publish/post/{d_id}")
            return res_json
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        print(f"[-] Error HTTP de Substack ({e.code}): {err_msg}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[-] Error al comunicarse con Substack: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Publicador automatizado de Última Prensa para Substack y n8n."
    )
    parser.add_argument("--archivo", "-a", required=True, help="Ruta al archivo .html o .md")
    parser.add_argument("--titulo", "-t", default="", help="Título del artículo (opcional si está en el archivo)")
    parser.add_argument("--bajada", "-b", default="", help="Subtítulo o bajada")
    parser.add_argument("--modo", choices=["n8n", "directo"], default="directo", help="Vía de envío")
    parser.add_argument("--webhook", default=N8N_WEBHOOK_URL, help="URL del webhook en n8n")
    parser.add_argument("--publicacion", default=SUBSTACK_SUBDOMAIN, help="Subdominio de Substack")
    parser.add_argument("--token", default=SUBSTACK_SID, help="Cookie substack.sid")
    parser.add_argument("--draft-id", default=None, type=int, help="ID de borrador existente a actualizar (opcional)")

    args = parser.parse_args()
    ruta = Path(args.archivo).resolve()
    if not ruta.exists():
        print(f"[-] Error: El archivo {ruta} no existe.", file=sys.stderr)
        sys.exit(1)

    t_extraido, b_extraido, html_content = extraer_metadatos_archivo(ruta)
    titulo_final = args.titulo or t_extraido or "Reportaje Especial de Última Prensa"
    subtitulo_final = args.bajada or b_extraido or ""

    print("==================================================")
    print("Última Prensa — Publicador Automatizado a Substack")
    print("==================================================")
    print(f"Artículo:    {ruta.name}")
    print(f"Título:      {titulo_final}")
    print(f"Subtítulo:   {subtitulo_final}")
    print(f"Publicación: https://{args.publicacion}.substack.com")
    print(f"Modo:        {args.modo}")
    if args.draft_id:
        print(f"Borrador ID: {args.draft_id} (Actualización in-place)")
    print("--------------------------------------------------")

    if args.modo == "n8n":
        enviar_a_n8n(
            titulo=titulo_final,
            subtitulo=subtitulo_final,
            html=html_content,
            token=args.token,
            publicacion=args.publicacion,
            webhook_url=args.webhook
        )
    elif args.modo == "directo":
        enviar_directo_substack(
            titulo=titulo_final,
            subtitulo=subtitulo_final,
            html=html_content,
            token=args.token,
            publicacion=args.publicacion,
            draft_id=args.draft_id
        )

if __name__ == "__main__":
    main()
