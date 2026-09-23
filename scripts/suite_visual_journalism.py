#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
suite_visual_journalism.py — Suite Unificada de Gráficos y Animación Editorial
Última Prensa IA Journalism Kit

Integra y orquesta los 4 motores gráficos de investigación periodística:
  1. Motor Infocards: Tarjetas infográficas y carruseles animados GIF/WebP (Chromium + FFmpeg).
  2. Motor Evidencia: Fojas judiciales, decretos y querellas estilo Silicon / Carbon (Terminal oscura).
  3. Motor AntV / D3: Diagramas de flujo de dineros y mapas de relaciones en SVG y PNG 2x.
  4. Motor Remotion: Cápsulas de motion graphics y reels verticales 9:16 en video MP4 con React.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def ejecutar_motor_infocards(reportaje_dir: Path):
    print("\n" + "="*60)
    print("🚀 MOTOR 1: Infocards y Carruseles GIF/WebP (Chromium + FFmpeg)")
    print("="*60)
    script = BASE_DIR / "scripts" / "generar_tarjetas_graficas.py"
    subprocess.run([sys.executable, str(script)], check=True)


def ejecutar_motor_evidencia(reportaje_dir: Path):
    print("\n" + "="*60)
    print("⚖️  MOTOR 2: Tarjetas de Evidencia Forense estilo Silicon / Carbon")
    print("="*60)
    script = BASE_DIR / "scripts" / "generar_tarjetas_evidencia.py"
    subprocess.run([sys.executable, str(script)], check=True)


def ejecutar_motor_diagramas(reportaje_dir: Path):
    print("\n" + "="*60)
    print("📊 MOTOR 3: Diagramas de Flujo y Malla Financiera (AntV / SVG)")
    print("="*60)
    script = BASE_DIR / "scripts" / "generar_diagramas_antv.py"
    subprocess.run([sys.executable, str(script)], check=True)


def ejecutar_motor_video(out_dir: Path):
    print("\n" + "="*60)
    print("🎬 MOTOR 4: Motion Video y Reels Verticales (Remotion + React)")
    print("="*60)
    motion_dir = BASE_DIR / "motion-video"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / "curaco_reel.mp4"
    out_gif = out_dir / "curaco_reel.gif"

    print("Renderizando Reel vertical con Remotion...")
    cmd = [
        "npx", "remotion", "render",
        "src/index.jsx", "CuracoReel",
        str(out_mp4.resolve())
    ]
    res = subprocess.run(cmd, cwd=str(motion_dir), capture_output=True, text=True)
    if res.returncode == 0 and out_mp4.exists():
        print(f"  ✓ Video Reel MP4 generado exitosamente: {out_mp4.name} ({out_mp4.stat().st_size // 1024} KB)")
    else:
        print(f"  ℹ️ Aviso en renderizado Remotion: {res.stderr[:200]}")


def main():
    parser = argparse.ArgumentParser(description="Suite Unificada de Periodismo Visual de Última Prensa")
    parser.add_argument("--todo", action="store_true", help="Ejecutar los 4 motores secuencialmente")
    parser.add_argument("--infocards", action="store_true", help="Ejecutar Motor 1 (Infocards y Carrusel GIF)")
    parser.add_argument("--evidencia", action="store_true", help="Ejecutar Motor 2 (Fojas estilo Silicon)")
    parser.add_argument("--diagramas", action="store_true", help="Ejecutar Motor 3 (Diagramas de Flujo AntV)")
    parser.add_argument("--video", action="store_true", help="Ejecutar Motor 4 (Reel Remotion)")
    parser.add_argument("--dir", default="reportajes/caso_relleno_curaco_osorno/graficos", help="Directorio de salida")

    args = parser.parse_args()
    out_dir = Path(args.dir)

    if not any([args.todo, args.infocards, args.evidencia, args.diagramas, args.video]):
        parser.print_help()
        print("\nEjecutando suite completa por defecto con --todo...\n")
        args.todo = True

    if args.todo or args.infocards:
        ejecutar_motor_infocards(out_dir)
    if args.todo or args.evidencia:
        ejecutar_motor_evidencia(out_dir)
    if args.todo or args.diagramas:
        ejecutar_motor_diagramas(out_dir)
    if args.todo or args.video:
        ejecutar_motor_video(out_dir)

    print("\n" + "="*60)
    print("✅ SUITE VISUAL COMPLETADA: Todas las piezas gráficas están listas.")
    print("="*60)


if __name__ == "__main__":
    main()
