#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline_editorial.py — Andamiaje y control de la producción editorial diaria.

No investiga ni escribe: eso lo hace el agente. Este script se encarga de la
parte mecánica y verificable del ciclo diario —abrir el expediente del día,
leer la agenda, marcar etapas, lanzar el pase editorial a un CLI, correr los
controles de calidad y cerrar con un resumen— para que el estado del trabajo
viva en disco y no en el historial de una conversación.

Estructura de cada caso (igual a la de iniciar_reportaje.py):

    reportajes/<slug>/
        brief.md            agenda del día completa
        estado.json         qué etapas están hechas y cuándo
        radar.md            noticias y pistas encontradas (lo escribe el agente)
        dossier.md          hechos verificados con fuente
        legal.md            contexto jurídico (open-legal-chile)
        borrador.md         texto en progreso
        pase_*.md           salida del pase editorial con Opus
        qa_resultado.md     controles automáticos
        cierre.md           resumen final y pendientes
        documentos/ fuentes/ notas_y_datos/

Uso:
    python scripts/pipeline_editorial.py abrir   --fecha 2026-10-27
    python scripts/pipeline_editorial.py estado  --fecha 2026-10-27
    python scripts/pipeline_editorial.py marcar  --fecha 2026-10-27 --etapa dossier
    python scripts/pipeline_editorial.py pase    --fecha 2026-10-27 --tarea pase_completo
    python scripts/pipeline_editorial.py qa      --fecha 2026-10-27
    python scripts/pipeline_editorial.py cerrar  --fecha 2026-10-27

Variables de entorno:
    ULTIMAPRENSA_REPORTAJES   raíz de reportajes (para pruebas)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent.parent          # kit-journalism/
PROYECTO = BASE.parent                                  # Ultimaprensa/
REPORTAJES = Path(os.environ.get("ULTIMAPRENSA_REPORTAJES", PROYECTO / "reportajes"))
AGENDA = REPORTAJES / "_agenda"

ETAPAS = ["agenda", "cobertura", "legal", "dossier", "borrador", "pase", "qa", "cierre"]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def slug(texto: str) -> str:
    limpio = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode()
    limpio = "".join(c if c.isalnum() or c.isspace() else " " for c in limpio)
    return "_".join(limpio.lower().split())[:60] or "sin_titulo"


def carpeta_agenda(fecha: str) -> Path:
    return AGENDA / f"{fecha}.md"


def leer_agenda(fecha: str) -> dict:
    """Lee el frontmatter YAML de la agenda del día."""
    ruta = carpeta_agenda(fecha)
    if not ruta.exists():
        sys.exit(
            f"No hay agenda para {fecha}.\n"
            f"  Crea el archivo copiando la plantilla:\n"
            f"    cp {AGENDA / '_plantilla.md'} {ruta}\n"
            "  Sin agenda el agente solo propone temas, no investiga."
        )
    texto = ruta.read_text(encoding="utf-8")
    if not texto.startswith("---"):
        sys.exit(f"La agenda {ruta} no tiene frontmatter YAML entre líneas ---")
    _, frontal, cuerpo = texto.split("---", 2)
    datos = yaml.safe_load(frontal) or {}
    if not datos.get("tema"):
        sys.exit(f"La agenda {ruta} no define 'tema'. Sin tema no se abre el caso.")
    tipo = (datos.get("tipo") or "nota").strip().lower()
    if tipo not in ("reportaje", "nota"):
        sys.exit(f"Tipo inválido en la agenda: '{tipo}'. Usa 'reportaje' o 'nota'.")
    datos["tipo"] = tipo
    datos["_cuerpo"] = cuerpo.strip()
    datos["_ruta"] = str(ruta)
    return datos


def carpeta_caso(fecha: str, datos: dict) -> Path:
    """La carpeta lleva la fecha para que el orden cronológico sea evidente."""
    return REPORTAJES / f"{fecha}_{slug(datos['tema'])}"


def crear_estructura(destino: Path) -> None:
    for sub in ("documentos", "fuentes", "notas_y_datos"):
        (destino / sub).mkdir(parents=True, exist_ok=True)
        (destino / sub / ".gitkeep").touch()


def cargar_estado(caso: Path) -> dict:
    ruta = caso / "estado.json"
    if not ruta.exists():
        return {}
    return json.loads(ruta.read_text(encoding="utf-8"))


def guardar_estado(caso: Path, estado: dict) -> None:
    estado["actualizado"] = time.strftime("%Y-%m-%d %H:%M:%S")
    (caso / "estado.json").write_text(
        json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")


def escribir_brief(caso: Path, datos: dict, fecha: str) -> None:
    lineas = [f"# Brief editorial — {fecha}", ""]
    for clave in ("tipo", "tema", "angulo", "extension"):
        if datos.get(clave):
            lineas.append(f"- **{clave}:** {datos[clave]}")
    for clave, rotulo in (("apuntar_a", "Dónde apuntar"), ("fuentes_clave", "Fuentes clave"),
                          ("no_tocar", "No tocar")):
        valores = datos.get(clave) or []
        if valores:
            lineas += ["", f"## {rotulo}"]
            lineas += [f"- {v}" for v in valores]
    if datos.get("_cuerpo"):
        lineas += ["", "## Notas del editor", "", datos["_cuerpo"]]
    (caso / "brief.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------
def comando_abrir(fecha: str, tema: str | None, tipo: str | None) -> int:
    """Abre el expediente del día. Si el tema viene por parámetro y no hay agenda,
    la crea: así el ciclo se dispara desde el chat sin editar archivos a mano."""
    if tema and not carpeta_agenda(fecha).exists():
        comando_agenda(fecha, tipo or "nota")
        ruta = carpeta_agenda(fecha)
        texto = ruta.read_text(encoding="utf-8").replace('tema: ""', f'tema: "{tema}"', 1)
        ruta.write_text(texto, encoding="utf-8")
    datos = leer_agenda(fecha)
    caso = carpeta_caso(fecha, datos)
    if (caso / "estado.json").exists():
        print(f"El caso de {fecha} ya está abierto: {caso}")
        return comando_estado(fecha)
    crear_estructura(caso)
    escribir_brief(caso, datos, fecha)
    guardar_estado(caso, {
        "fecha": fecha,
        "tipo": datos["tipo"],
        "tema": datos["tema"],
        "extension_objetivo": str(datos.get("extension") or ""),
        "etapas": {e: ("ok" if e == "agenda" else "pendiente") for e in ETAPAS},
    })
    print(f"Caso abierto: {caso}")
    print(f"  tipo: {datos['tipo']}  ·  tema: {datos['tema']}")
    print(f"  brief: {caso / 'brief.md'}")
    return 0


def comando_marcar(fecha: str, etapa: str, nota: str | None) -> int:
    if etapa not in ETAPAS:
        sys.exit(f"Etapa desconocida: {etapa}. Válidas: {', '.join(ETAPAS)}")
    datos = leer_agenda(fecha)
    caso = carpeta_caso(fecha, datos)
    estado = cargar_estado(caso)
    if not estado:
        sys.exit(f"El caso no está abierto. Corre primero: pipeline_editorial.py abrir --fecha {fecha}")
    estado["etapas"][etapa] = "ok"
    if nota:
        estado.setdefault("notas", {})[etapa] = nota
    guardar_estado(caso, estado)
    print(f"{etapa}: ok")
    return 0


def comando_estado(fecha: str) -> int:
    datos = leer_agenda(fecha)
    caso = carpeta_caso(fecha, datos)
    estado = cargar_estado(caso)
    if not estado:
        print(f"El caso de {fecha} no está abierto ({caso}).")
        return 1
    print(f"Caso: {caso.name}")
    print(f"  tipo {estado.get('tipo')} · tema: {estado.get('tema')}")
    print()
    for etapa in ETAPAS:
        marca = "ok " if estado["etapas"].get(etapa) == "ok" else "-- "
        archivo = caso / f"{etapa}.md"
        extra = f"   ({archivo.name} presente)" if archivo.exists() else ""
        print(f"  [{marca}] {etapa}{extra}")
    pendientes = [e for e in ETAPAS if estado["etapas"].get(e) != "ok"]
    print()
    print("  Siguiente etapa: " + (pendientes[0] if pendientes else "ninguna: cerrado"))
    return 0


def _material(caso: Path, limite: int = 120_000) -> tuple[str, str]:
    """Devuelve (texto, origen). Prefiere el borrador; si no, junta las notas."""
    borrador = caso / "borrador.md"
    if borrador.exists():
        return borrador.read_text(encoding="utf-8")[:limite], borrador.name
    partes, total = [], 0
    for ruta in sorted(caso.rglob("*.md")):
        if ruta.name.startswith(("pase_", "qa_resultado", "cierre")):
            continue
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        if total + len(texto) > limite:
            break
        partes.append(f"\n\n<!-- {ruta.relative_to(caso)} -->\n\n{texto}")
        total += len(texto)
    return "".join(partes), f"{len(partes)} archivos del expediente"


def comando_pase(fecha: str, tarea: str, motor: str, modelo: str | None) -> int:
    datos = leer_agenda(fecha)
    caso = carpeta_caso(fecha, datos)
    estado = cargar_estado(caso)
    if not estado:
        sys.exit(f"El caso no está abierto. Abre primero con: abrir --fecha {fecha}")
    contenido, origen = _material(caso)
    if not contenido.strip():
        sys.exit("No hay material para pasar: falta borrador.md y notas en el expediente.")

    comando = [sys.executable, str(BASE / "scripts" / "nvidia_router.py"), "derivar",
               "--motor", motor, "--tarea", tarea, "--workdir", str(caso / "pases")]
    if modelo:
        comando += ["--modelo", modelo]
    proceso = subprocess.run(comando, input=contenido, capture_output=True, text=True,
                             cwd=str(PROYECTO))
    if proceso.returncode != 0:
        print(proceso.stderr.strip()[-1200:] or "El pase falló sin mensaje.", file=sys.stderr)
        return 1
    marca = time.strftime("%Y%m%d_%H%M%S")
    salida = caso / f"pase_{tarea}_{marca}.md"
    salida.write_text(f"<!-- motor: {motor} · tarea: {tarea} · material: {origen} -->\n\n"
                      + proceso.stdout, encoding="utf-8")
    detalle = proceso.stderr.strip().splitlines()
    print(f"Pase escrito en {salida}")
    if detalle:
        print("  " + detalle[-1])
    estado["etapas"]["pase"] = "ok"
    guardar_estado(caso, estado)
    return 0


VALIDACIONES = [
    ("redundancia", "detector_redundancia_lexica.py"),
    ("ortografía", "revisar_languagetool.py"),
    ("verificación", "verificar_reportaje.py"),
]


def comando_qa(fecha: str) -> int:
    datos = leer_agenda(fecha)
    caso = carpeta_caso(fecha, datos)
    borrador = caso / "borrador.md"
    if not borrador.exists():
        sys.exit(f"No hay borrador que revisar en {caso}. El QA corre sobre borrador.md.")
    lineas = [f"# Controles automáticos — {fecha}", ""]
    fallos = 0
    for nombre, script in VALIDACIONES:
        ruta = BASE / "scripts" / script
        if not ruta.exists():
            lineas.append(f"- **{nombre}:** no disponible ({script} no existe)")
            continue
        proceso = subprocess.run([sys.executable, str(ruta), str(borrador)],
                                 capture_output=True, text=True, cwd=str(PROYECTO))
        estado_txt = "sin observaciones" if proceso.returncode == 0 else "con observaciones"
        if proceso.returncode != 0:
            fallos += 1
        salida = (proceso.stdout + proceso.stderr).strip()
        lineas += [f"## {nombre} — {estado_txt}", "", "```", salida[:6000] or "(sin salida)", "```", ""]
    (caso / "qa_resultado.md").write_text("\n".join(lineas), encoding="utf-8")
    print(f"QA escrito en {caso / 'qa_resultado.md'} · {fallos} de {len(VALIDACIONES)} "
          f"controles con observaciones")
    estado = cargar_estado(caso)
    estado["etapas"]["qa"] = "ok"
    guardar_estado(caso, estado)
    return 0


def comando_cerrar(fecha: str) -> int:
    datos = leer_agenda(fecha)
    caso = carpeta_caso(fecha, datos)
    estado = cargar_estado(caso)
    if not estado:
        sys.exit(f"El caso no está abierto: {caso}")
    pendientes = [e for e in ETAPAS if estado["etapas"].get(e) != "ok"]
    archivos = sorted(p.name for p in caso.glob("*.md"))
    lineas = [
        f"# Cierre — {fecha}",
        "",
        f"- **Tipo:** {estado.get('tipo')}",
        f"- **Tema:** {estado.get('tema')}",
        f"- **Carpeta:** `{caso}`",
        "",
        "## Archivos del expediente",
        "",
        *[f"- {a}" for a in archivos],
        "",
        "## Etapas",
        "",
        *[f"- [{'x' if estado['etapas'].get(e) == 'ok' else ' '}] {e}" for e in ETAPAS],
        "",
        ("## Pendientes\n\n" + "\n".join(f"- {p}" for p in pendientes)) if pendientes
        else "## Sin pendientes de etapa\n\nFalta la revisión y aprobación del editor.",
        "",
        "> Este cierre es mecánico: no certifica la verificación periodística. La firma",
        "> editorial y la comprobación de fuentes siguen siendo humanas.",
    ]
    (caso / "cierre.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    estado["etapas"]["cierre"] = "ok"
    guardar_estado(caso, estado)
    print(f"Cierre escrito en {caso / 'cierre.md'}")
    return 0


def comando_agenda(fecha: str, tipo: str | None) -> int:
    """Crea la agenda del día desde la plantilla, con el tipo según el día."""
    AGENDA.mkdir(parents=True, exist_ok=True)
    destino = carpeta_agenda(fecha)
    if destino.exists():
        print(f"La agenda de {fecha} ya existe: {destino}")
        print("  Editá ese archivo; no se sobrescribe.")
        return 0
    plantilla = AGENDA / "_plantilla.md"
    if not plantilla.exists():
        sys.exit(f"Falta la plantilla: {plantilla}")
    # Lunes y miércoles son día de reportaje grande; el resto, nota diaria.
    if not tipo:
        try:
            anio, mes, dia = (int(p) for p in fecha.split("-"))
            tipo = "reportaje" if date(anio, mes, dia).weekday() in (0, 2) else "nota"
        except ValueError:
            sys.exit(f"Fecha inválida: {fecha}. Usa AAAA-MM-DD.")
    if tipo not in ("reportaje", "nota"):
        sys.exit(f"Tipo inválido: {tipo}. Usa 'reportaje' o 'nota'.")
    texto = plantilla.read_text(encoding="utf-8")
    texto = texto.replace("tipo: nota                    #",
                          f"tipo: {tipo}" + " " * max(0, 21 - len(tipo)) + "#", 1)
    destino.write_text(texto, encoding="utf-8")
    print(f"Agenda creada: {destino}  (tipo {tipo})")
    print("  Completá tema, angulo, apuntar_a y fuentes_clave antes de las 07:00.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Andamiaje y control del ciclo editorial diario de Última Prensa")
    parser.add_argument("comando", choices=["agenda", "abrir", "estado", "marcar", "pase", "qa",
                                           "cerrar"])
    parser.add_argument("--fecha", default=date.today().isoformat(),
                        help="AAAA-MM-DD (por defecto, hoy)")
    parser.add_argument("--etapa", help="para 'marcar': etapa completada")
    parser.add_argument("--nota", help="para 'marcar': comentario opcional")
    parser.add_argument("--tarea", default="pase_completo",
                        help="para 'pase': tarea del router (pase_completo, pase_final, apertura…)")
    parser.add_argument("--motor", default="claude", help="para 'pase': claude | agy")
    parser.add_argument("--modelo", help="para 'pase': fuerza un modelo del CLI")
    parser.add_argument("--tipo", choices=["reportaje", "nota"],
                        help="para 'agenda' y 'abrir': fuerza el tipo (por defecto, lunes y "
                             "miércoles son reportaje y el resto nota)")
    parser.add_argument("--tema", help="para 'abrir': abre un caso nuevo con este tema, creando "
                                      "la agenda si no existe")
    args = parser.parse_args()

    if args.comando == "agenda":
        return comando_agenda(args.fecha, args.tipo)
    if args.comando == "abrir":
        return comando_abrir(args.fecha, args.tema, args.tipo)
    if args.comando == "estado":
        return comando_estado(args.fecha)
    if args.comando == "marcar":
        if not args.etapa:
            parser.error("marcar requiere --etapa")
        return comando_marcar(args.fecha, args.etapa, args.nota)
    if args.comando == "pase":
        return comando_pase(args.fecha, args.tarea, args.motor, args.modelo)
    if args.comando == "qa":
        return comando_qa(args.fecha)
    return comando_cerrar(args.fecha)


if __name__ == "__main__":
    sys.exit(main())
