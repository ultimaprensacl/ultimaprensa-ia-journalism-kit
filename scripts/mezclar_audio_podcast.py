#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mezclar_audio_podcast.py — Motor de Mezcla y Post-Producción Multipista para Última Prensa.
Parte del kit oficial ultimaprensa-ia-journalism-kit.

Combina locución con música de fondo ambiental, aplicando:
  - Volumen dinámico (ducking periodístico a -23 dB durante locución activa).
  - Intro y cortina de apertura (-8 dB con fade-in).
  - Cierre y cortina final (-10 dB con fade-out).
  - Masterización broadcast final conforme a EBU R128 (-16 LUFS, 48 kHz).
"""

import sys
import argparse
import subprocess
from pathlib import Path
from pydub import AudioSegment

def mezclar_podcast(voz_path: Path, bgm_path: Path, out_path: Path, ducking_db: float = -23.0, intro_offset_ms: int = 2500):
    print(f"[*] Cargando locución: {voz_path.name}...")
    voz = AudioSegment.from_file(str(voz_path))
    dur_voz_ms = len(voz)
    print(f"    - Duración locución: {dur_voz_ms / 1000 / 60:.2f} min ({dur_voz_ms / 1000:.1f} s)")

    print(f"[*] Cargando música de fondo: {bgm_path.name}...")
    bgm_segment = AudioSegment.from_file(str(bgm_path))
    
    voz = voz.set_channels(2).set_frame_rate(44100)
    bgm_segment = bgm_segment.set_channels(2).set_frame_rate(44100)

    # Cobertura musical completa + 6s de outro
    target_dur_ms = dur_voz_ms + 6000
    loops_needed = int(target_dur_ms / len(bgm_segment)) + 2
    
    musica_completa = AudioSegment.empty()
    for _ in range(loops_needed):
        if len(musica_completa) == 0:
            musica_completa = bgm_segment
        else:
            musica_completa = musica_completa.append(bgm_segment, crossfade=1500)
            
    musica_completa = musica_completa[:target_dur_ms]

    # Ducking dinámico
    parte_intro = (musica_completa[:4500] - 8).fade_in(1000)
    parte_cuerpo = musica_completa[4500:dur_voz_ms - 6000] + ducking_db
    parte_outro = (musica_completa[dur_voz_ms - 6000:] - 10).fade_out(4000)
    
    pista_musical = parte_intro.append(parte_cuerpo, crossfade=1200).append(parte_outro, crossfade=1200)
    pista_musical = pista_musical[:target_dur_ms]

    print(f"[*] Superponiendo pistas (ducking {ducking_db} dB, retardo intro {intro_offset_ms} ms)...")
    lienzo = AudioSegment.silent(duration=target_dur_ms)
    lienzo = lienzo.overlay(pista_musical, position=0)
    lienzo = lienzo.overlay(voz + 1.0, position=intro_offset_ms)

    temp_export = out_path.parent / "temp_pre_master.wav"
    lienzo.export(str(temp_export), format="wav")

    print("[*] Masterizando mezcla con FFmpeg (EBU R128 -16 LUFS)...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_export),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=10",
        "-b:a", "192k",
        "-ar", "48000",
        str(out_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and out_path.exists():
        sz = out_path.stat().st_size // 1024
        print(f"[✓] Master final masterizado con éxito: {out_path.name} ({sz} KB)")
        if temp_export.exists():
            temp_export.unlink()
    else:
        print(f"[-] Error en FFmpeg: {res.stderr}", file=sys.stderr)

    res_dur = subprocess.run([
        "ffprobe", "-i", str(out_path),
        "-show_entries", "format=duration",
        "-v", "quiet", "-of", "csv=p=0"
    ], capture_output=True, text=True)
    if res_dur.returncode == 0 and res_dur.stdout.strip():
        dur_s = float(res_dur.stdout.strip())
        print(f"[✓] Duración final con cortinas y ducking: {int(dur_s//60):02d}:{int(dur_s%60):02d} min ({dur_s:.1f} s)")

def main():
    parser = argparse.ArgumentParser(description="Mezclador de audio y música con ducking dinámico para Última Prensa")
    parser.add_argument("--voz", required=True, help="Ruta al archivo de voz/locución (.wav o .mp3)")
    parser.add_argument("--musica", required=True, help="Ruta a la música de fondo instrumental (.wav o .mp3)")
    parser.add_argument("--salida", required=True, help="Ruta de destino del master final (.mp3)")
    parser.add_argument("--ducking", type=float, default=-23.0, help="Atenuación de la música en dB durante el habla (default: -23 dB)")
    parser.add_argument("--intro-offset", type=int, default=2500, help="Milisegundos de música sola antes de que empiece la locución (default: 2500)")

    args = parser.parse_args()
    voz_path = Path(args.voz).resolve()
    musica_path = Path(args.musica).resolve()
    salida_path = Path(args.salida).resolve()

    if not voz_path.exists():
        print(f"[-] Error: Archivo de voz no encontrado: {voz_path}", file=sys.stderr)
        sys.exit(1)
    if not musica_path.exists():
        print(f"[-] Error: Archivo de música no encontrado: {musica_path}", file=sys.stderr)
        sys.exit(1)

    salida_path.parent.mkdir(parents=True, exist_ok=True)
    mezclar_podcast(voz_path, musica_path, salida_path, ducking_db=args.ducking, intro_offset_ms=args.intro_offset)

if __name__ == "__main__":
    main()
