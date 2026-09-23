#!/usr/bin/env python3
"""
Última Prensa — Extractor y Desenrollador de Hilos de Twitter / X
Permite extraer el contenido completo de tuits e hilos de conversación en Twitter / X
utilizando APIs de sindicación libres (FxTwitter y VxTwitter) sin requerir claves de API
ni inicio de sesión.
"""

import sys
import os
import re
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional


def extraer_tweet_id(url_o_id: str) -> Optional[str]:
    """Extrae el ID numérico del tuit a partir de una URL o del ID en bruto."""
    url_o_id = url_o_id.strip()
    match = re.search(r"status/(\d+)", url_o_id)
    if match:
        return match.group(1)
    if url_o_id.isdigit():
        return url_o_id
    return None


def obtener_tweet_vxtwitter(tweet_id: str) -> Optional[Dict[str, Any]]:
    """Consulta la API pública de VxTwitter para obtener los datos del tuit."""
    url = f"https://api.vxtwitter.com/status/{tweet_id}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data
    except Exception as e:
        sys.stderr.write(f"Aviso VxTwitter ({tweet_id}): {e}\n")
    return None


def obtener_tweet_fxtwitter(tweet_id: str) -> Optional[Dict[str, Any]]:
    """Consulta la API pública de FxTwitter como alternativa."""
    url = f"https://api.fxtwitter.com/status/{tweet_id}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("code") == 200 and data.get("tweet"):
                    t = data["tweet"]
                    # Normalizar a estructura común
                    author = t.get("author", {})
                    media_urls = []
                    if "media" in t and "all" in t["media"]:
                        for m in t["media"]["all"]:
                            if "url" in m:
                                media_urls.append(m["url"])
                    return {
                        "tweetID": t.get("id"),
                        "text": t.get("text", ""),
                        "user_name": author.get("name", ""),
                        "user_screen_name": author.get("screen_name", ""),
                        "date": t.get("created_at", ""),
                        "replyingToID": t.get("replying_to_status"),
                        "mediaURLs": media_urls,
                        "likes": t.get("likes", 0),
                        "retweets": t.get("retweets", 0),
                        "replies": t.get("replies", 0),
                        "tweetURL": t.get("url", f"https://x.com/status/{tweet_id}"),
                    }
    except Exception as e:
        sys.stderr.write(f"Aviso FxTwitter ({tweet_id}): {e}\n")
    return None


def obtener_tweet(tweet_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene los datos del tuit probando VxTwitter primero y FxTwitter de respaldo."""
    data = obtener_tweet_vxtwitter(tweet_id)
    if data and data.get("text"):
        return data
    data_fx = obtener_tweet_fxtwitter(tweet_id)
    if data_fx:
        return data_fx
    return data


def desenrollar_hilo_hacia_atras(tweet_id_final: str, max_profundidad: int = 50) -> List[Dict[str, Any]]:
    """
    Si se proporciona el último tuit del hilo, rastrea recursivamente la cadena de
    tuits ascendente (replyingToID) del mismo autor para reconstruir el hilo en orden cronológico.
    """
    hilo = []
    actual_id = tweet_id_final
    autor_original = None

    for _ in range(max_profundidad):
        if not actual_id:
            break
        tweet = obtener_tweet(actual_id)
        if not tweet:
            break

        usuario = tweet.get("user_screen_name")
        if autor_original is None:
            autor_original = usuario

        hilo.append(tweet)

        # Si el autor cambia o no tiene respuesta previa, terminamos la cadena
        padre_id = tweet.get("replyingToID")
        if not padre_id:
            break

        # Si el tuit responde a otra persona diferente, detenemos la cadena del hilo propio
        padre_usuario = tweet.get("replyingTo")
        if padre_usuario and autor_original and padre_usuario.lower() != autor_original.lower():
            # Si responde a otro autor, podríamos incluir el padre o detenernos
            break

        actual_id = str(padre_id)

    # Invertir para que quede en orden cronológico (del primero al último)
    hilo.reverse()
    return hilo


def formatear_hilo_markdown(hilo: List[Dict[str, Any]]) -> str:
    """Convierte una lista de tuits en un informe Markdown estructurado."""
    if not hilo:
        return "No se pudo recuperar la información del tuit o hilo."

    primer_tweet = hilo[0]
    autor = primer_tweet.get("user_name", "Desconocido")
    handle = primer_tweet.get("user_screen_name", "anon")
    fecha = primer_tweet.get("date", "")
    url_raiz = primer_tweet.get("tweetURL", "")

    md = []
    md.append(f"# Hilo de @{handle} ({autor})\n")
    md.append(f"- **Autor:** {autor} ([@{handle}](https://x.com/{handle}))")
    md.append(f"- **Fecha inicial:** {fecha}")
    md.append(f"- **Enlace original:** {url_raiz}")
    md.append(f"- **Cantidad de mensajes analizados:** {len(hilo)}")
    md.append("\n---\n")

    for idx, t in enumerate(hilo, 1):
        num_str = f"**[{idx}/{len(hilo)}]**" if len(hilo) > 1 else "**[Tuit]**"
        t_id = t.get("tweetID", "")
        t_url = t.get("tweetURL", f"https://x.com/{handle}/status/{t_id}")
        t_fecha = t.get("date", "")
        t_texto = t.get("text", "").strip()
        t_likes = t.get("likes", 0)
        t_rt = t.get("retweets", 0)

        md.append(f"### {num_str} — {t_fecha}")
        md.append(f"\n{t_texto}\n")

        # Multimedia
        media = t.get("mediaURLs", [])
        if media:
            md.append("**Archivos adjuntos:**")
            for m in media:
                if any(m.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    md.append(f"- ![Imagen]({m})")
                else:
                    md.append(f"- [Elemento multimedia]({m})")
            md.append("")

        # Métricas
        md.append(f"> ❤️ {t_likes:,} · 🔁 {t_rt:,} · [Ver en X]({t_url})\n")
        md.append("---\n")

    return "\n".join(md)


def main():
    if len(sys.argv) < 2:
        print("Uso: python leer_hilo_twitter.py <URL_O_ID_DEL_TWEET> [--salida archivo.md]")
        print("Ejemplo: python leer_hilo_twitter.py https://x.com/jack/status/20")
        sys.exit(1)

    url_o_id = sys.argv[1]
    tweet_id = extraer_tweet_id(url_o_id)

    if not tweet_id:
        print(f"Error: No se pudo identificar un ID de tuit válido en: {url_o_id}")
        sys.exit(1)

    archivo_salida = None
    if "--salida" in sys.argv:
        idx = sys.argv.index("--salida")
        if idx + 1 < len(sys.argv):
            archivo_salida = sys.argv[idx + 1]

    print(f"🔍 Consultando tuit/hilo ID {tweet_id}...")
    hilo = desenrollar_hilo_hacia_atras(tweet_id)

    if not hilo:
        print("❌ No se pudo obtener el tuit. Verifica que el tuit sea público y exista.")
        sys.exit(1)

    md = formatear_hilo_markdown(hilo)

    if archivo_salida:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"✅ Hilo guardado exitosamente en: {archivo_salida}")
    else:
        print("\n" + md)


if __name__ == "__main__":
    main()
