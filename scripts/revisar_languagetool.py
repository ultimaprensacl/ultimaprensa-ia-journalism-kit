#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
revisar_languagetool.py — Módulo de gramática y ortografía en español con LanguageTool, sin conexión.

Revisa el cuerpo de un reportaje en Markdown (titular, bajada y texto; sin imágenes, direcciones de
enlaces ni la sección de fuentes) con LanguageTool instalado localmente, y lista cada observación con
su contexto y sugerencias. Nada sale del computador.

Uso:
    python kit-journalism/scripts/revisar_languagetool.py <reportaje.md> [--con-fuentes] [--todo]
    python kit-journalism/scripts/revisar_languagetool.py --autoprueba

Requisitos (rutas configurables por variables de entorno):
    LT_HOME  carpeta de LanguageTool  (por defecto ~/.local/opt/LanguageTool-6.6)
    LT_JAVA  ejecutable de Java 17+   (por defecto ~/.local/opt/jdk-21.0.13+9-jre/bin/java o `java`)

Devuelve código 1 si quedan observaciones, para poder usarlo antes de exportar a Substack.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

LT_HOME = Path(os.environ.get("LT_HOME", Path.home() / ".local/opt/LanguageTool-6.6"))
JAVA_LOCAL = Path.home() / ".local/opt/jdk-21.0.13+9-jre/bin/java"
LT_JAVA = os.environ.get("LT_JAVA") or (str(JAVA_LOCAL) if JAVA_LOCAL.exists() else shutil.which("java"))

# Palabras válidas en el español de Chile o en el léxico del medio que el diccionario de LanguageTool no trae.
PALABRAS_ACEPTADAS = {"subrogante", "subrogantes", "gerenta", "gerentas", "reajustabilidad", "exsubordinado",
                      "exsubordinada", "exconcejal", "exconcejala", "exalcalde", "exalcaldesa", "exfuncionario",
                      "exfuncionaria", "democratacristiano", "democratacristiana", "puertomontino", "puertomontina"}

# Reglas que chocan con el estilo de Última Prensa o generan ruido en Markdown convertido a texto.
REGLAS_DESACTIVADAS = [
    "WHITESPACE_RULE",            # espacios dobles que deja la conversión
    "UPPERCASE_SENTENCE_START",   # viñetas y pies que empiezan con cifra o signo
]


def markdown_a_texto(md: str, con_fuentes: bool) -> str:
    """Deja solo el texto que lee el público: sin imágenes, URLs, marcas ni (por defecto) fuentes."""
    if not con_fuentes:
        md = re.split(r"^#{2,3}\s+Fuentes documentales", md, flags=re.MULTILINE)[0]
    md = re.sub(r"```.*?```", " ", md, flags=re.DOTALL)
    parrafos = []
    for bloque in re.split(r"\n\s*\n", md):
        lineas = []
        for linea in bloque.splitlines():
            l = linea.strip()
            if not l or l.startswith("![") or re.fullmatch(r"-{3,}", l):
                continue
            l = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", l)          # imágenes en línea
            l = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", l)       # enlaces: deja el texto
            l = re.sub(r"https?://\S+", "", l)                   # URLs sueltas
            l = re.sub(r"^#{1,6}\s+", "", l)                      # encabezados
            l = re.sub(r"^>\s*", "", l)                           # citas en bloque
            l = re.sub(r"^(\*|-|\d+\.)\s+", "", l)                # viñetas y listas
            l = l.replace("**", "").replace("*", "")              # negritas y cursivas
            if l:
                lineas.append(l)
        if lineas:
            parrafos.append(" ".join(lineas))
    return "\n\n".join(parrafos)


def palabra_aceptada(match: dict, texto: str) -> bool:
    """Nombres propios (Lilayú, Wainraihgt, Verba…) y palabras de la lista del medio no son errores."""
    if match["rule"]["id"] != "MORFOLOGIK_RULE_ES":
        return False
    palabra = texto[match["offset"]: match["offset"] + match["length"]]
    return palabra[:1].isupper() or palabra.lower() in PALABRAS_ACEPTADAS


def dentro_de_cita(match: dict, texto: str) -> bool:
    """Las citas textuales entre « » no se corrigen: se informan aparte para revisar la transcripción."""
    abre = texto.rfind("«", 0, match["offset"])
    return abre != -1 and texto.find("»", abre) >= match["offset"] + match["length"]


def revisar(texto: str) -> list:
    if not LT_JAVA or not (LT_HOME / "languagetool-commandline.jar").exists():
        sys.exit(f"No encuentro LanguageTool en {LT_HOME} o Java ({LT_JAVA}). Revisa LT_HOME y LT_JAVA.")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as f:
        f.write(texto)
        ruta = f.name
    try:
        res = subprocess.run(
            [LT_JAVA, "-jar", str(LT_HOME / "languagetool-commandline.jar"), "-l", "es", "--json",
             "-d", ",".join(REGLAS_DESACTIVADAS), ruta],
            capture_output=True, text=True, timeout=600,
        )
    finally:
        os.unlink(ruta)
    salida = res.stdout[res.stdout.find("{"):]  # la herramienta a veces antepone avisos de Java
    if res.returncode != 0 or not salida:
        sys.exit(f"LanguageTool falló: {res.stderr.strip()[:500]}")
    return json.loads(salida)["matches"]


def autoprueba():
    """Comprueba que el módulo detecta errores reales y respeta citas y palabras aceptadas."""
    texto = markdown_a_texto("# Título\n\nLos diputado rindieron gastos. Hubieron facturas de la Camara. "
                             "El exsubordinado dijo «hubieron problemas».\n\n## Fuentes documentales\n\nNo revisar esto.", False)
    assert "No revisar" not in texto
    todos = revisar(texto)
    reglas = {m["rule"]["id"] for m in todos if not palabra_aceptada(m, texto) and not dentro_de_cita(m, texto)}
    assert {"AGREEMENT_DET_NOUN", "ID_HUBO_HUBIERON"} <= reglas, reglas
    assert any(dentro_de_cita(m, texto) for m in todos), "la cita textual debía quedar aparte"
    assert not any(texto[m["offset"]:m["offset"] + m["length"]] == "exsubordinado" and not palabra_aceptada(m, texto) for m in todos)
    print("Autoprueba OK")


def main():
    if "--autoprueba" in sys.argv:
        return autoprueba()
    ap = argparse.ArgumentParser(description="Módulo de gramática y ortografía (LanguageTool, español, sin conexión).")
    ap.add_argument("archivo", help="Reportaje en Markdown")
    ap.add_argument("--con-fuentes", action="store_true", help="Revisar también la sección de fuentes")
    ap.add_argument("--todo", action="store_true", help="No omitir nombres propios marcados como desconocidos")
    args = ap.parse_args()

    texto = markdown_a_texto(Path(args.archivo).read_text(encoding="utf-8"), args.con_fuentes)
    todos = revisar(texto)
    aceptados = [] if args.todo else [m for m in todos if palabra_aceptada(m, texto)]
    citas = [m for m in todos if m not in aceptados and dentro_de_cita(m, texto)]
    matches = [m for m in todos if m not in aceptados and m not in citas]

    print("=" * 70)
    print(f"MÓDULO LANGUAGETOOL (español, sin conexión): {Path(args.archivo).name}")
    print("=" * 70)
    print(f"Palabras revisadas: {len(texto.split())} | observaciones: {len(matches)} | "
          f"dentro de citas textuales: {len(citas)} | nombres propios y palabras aceptadas: {len(aceptados)}")
    for i, m in enumerate(matches, 1):
        ctx = m["context"]
        ini, fin = ctx["offset"], ctx["offset"] + ctx["length"]
        marcado = ctx["text"][:ini] + "⟦" + ctx["text"][ini:fin] + "⟧" + ctx["text"][fin:]
        sugerencias = ", ".join(r["value"] for r in m["replacements"][:3]) or "—"
        print(f"\n{i}. [{m['rule']['category']['name']}] {m['message']}")
        print(f"   …{marcado.strip()}…")
        print(f"   Sugerencias: {sugerencias}   (regla {m['rule']['id']})")
    if citas:
        print("\nDentro de citas textuales (no se corrigen; solo verificar que la transcripción sea fiel):")
        for m in citas:
            print(f"   · «{texto[m['offset']: m['offset'] + m['length']]}»: {m['message']}")
    if matches:
        print("\nResumen por regla:", dict(Counter(m["rule"]["id"] for m in matches).most_common()))
    print("=" * 70)
    sys.exit(1 if matches else 0)


if __name__ == "__main__":
    main()
