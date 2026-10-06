#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_podcast_investigacion.py — Motor de Síntesis y Masterización de Podcasts para Última Prensa.
Parte del kit oficial ultimaprensa-ia-journalism-kit.

Soporta dos backends 100% de código abierto / libres de telemetría:
  1. 'kokoro': Modelo neuronal local StyleTTS2 (82M ONNX) sin conexión a internet.
  2. 'edge': Voces neuronales de alta fidelidad (Álvaro Documental, Catalina Chile, etc.).
"""

import os
import re
import sys
import asyncio
import subprocess
import argparse
import time
from pathlib import Path

DEFAULT_MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "kokoro"

def extraer_texto_locucion(guion_path: Path) -> str:
    """Extrae exclusivamente los diálogos del locutor, omitiendo indicaciones técnicas y metadatos."""
    contenido = guion_path.read_text(encoding="utf-8")
    lineas = contenido.splitlines()
    
    texto_locucion = []
    en_locutor = False
    
    for linea in lineas:
        linea_str = linea.strip()
        if (linea_str.startswith("#") or linea_str.startswith("**Título") or 
            linea_str.startswith("**Serie") or linea_str.startswith("**Formato") or 
            linea_str.startswith("**Duración") or linea_str.startswith("**Tono") or 
            linea_str.startswith("---") or linea_str.startswith("###")):
            en_locutor = False
            continue
            
        if linea_str.startswith("**[AUDIO") or linea_str.startswith("[AUDIO"):
            en_locutor = False
            continue
            
        if (linea_str.startswith("**LOCUTOR:**") or linea_str.startswith("**LOCUTOR(A):**") or 
            linea_str.startswith("LOCUTOR:") or linea_str.startswith("LOCUTOR(A):")):
            en_locutor = True
            resto = re.sub(r"^\*{0,2}LOCUTOR(\([A-Z]\))?:\*{0,2}\s*", "", linea_str).strip()
            if resto:
                texto_locucion.append(resto)
            continue
            
        if en_locutor:
            if linea_str:
                linea_limpia = re.sub(r"\[.*?\]", "", linea_str).strip()
                if linea_limpia:
                    texto_locucion.append(linea_limpia)
            else:
                texto_locucion.append("\n")
                
    texto_final = "\n".join(texto_locucion).strip()
    return texto_final

def sintetizar_con_kokoro(texto: str, voz: str, out_wav: Path, model_dir: Path):
    """Sintetiza audio con el modelo local Kokoro ONNX."""
    from kokoro_onnx import Kokoro
    import soundfile as sf
    import numpy as np

    model_path = model_dir / "kokoro-v1.0.onnx"
    voices_path = model_dir / "voices-v1.0.bin"

    if not model_path.exists() or not voices_path.exists():
        print(f"[-] Error: Archivos del modelo Kokoro no encontrados en {model_dir}", file=sys.stderr)
        print("    Descargue kokoro-v1.0.onnx y voices-v1.0.bin en kit-journalism/models/kokoro/", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Inicializando Kokoro ONNX con voz '{voz}' (100% local en CPU)...")
    kokoro = Kokoro(str(model_path), str(voices_path))

    parrafos = [p.strip() for p in texto.split("\n") if p.strip()]
    print(f"[*] Procesando {len(parrafos)} párrafos con Kokoro...")

    audio_chunks = []
    sr = 24000
    silencio = np.zeros(int(sr * 0.45), dtype=np.float32)  # 450 ms de silencio interparrafal

    t0 = time.time()
    for idx, p in enumerate(parrafos, 1):
        p_clean = p.replace("«", "").replace("»", "").replace("—", ", ")
        try:
            samples, sample_rate = kokoro.create(p_clean, voice=voz, speed=0.92, lang="es")
            audio_chunks.append(samples)
            audio_chunks.append(silencio)
            if idx % 5 == 0 or idx == len(parrafos):
                print(f"  - Párrafo {idx}/{len(parrafos)} sintetizado ({time.time()-t0:.1f}s transcurridos)...")
        except Exception as e:
            print(f"  [!] Advertencia en párrafo {idx}: {e}", file=sys.stderr)

    full_audio = np.concatenate(audio_chunks)
    sf.write(str(out_wav), full_audio, sr)
    dur = len(full_audio) / sr
    print(f"[✓] Síntesis Kokoro finalizada: {dur/60:.2f} min ({dur:.1f}s) en {time.time()-t0:.1f}s.")

async def sintetizar_con_edge(texto: str, voz: str, velocidad: str, out_mp3: Path, out_srt: Path):
    """Sintetiza audio con Edge Neural TTS y genera subtítulos SRT sincronizados."""
    import edge_tts
    print(f"[*] Sintetizando con Edge Neural TTS ({voz}, velocidad: {velocidad})...")
    communicate = edge_tts.Communicate(texto, voz, rate=velocidad)
    submaker = edge_tts.SubMaker()

    with open(out_mp3, "wb") as f_mp3:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f_mp3.write(chunk["data"])
            else:
                submaker.feed(chunk)

    with open(out_srt, "w", encoding="utf-8") as f_srt:
        f_srt.write(submaker.get_srt())

    print(f"[✓] Audio crudo guardado en {out_mp3.name}")
    print(f"[✓] Subtítulos SRT sincronizados en {out_srt.name}")

def masterizar_audio(in_file: Path, out_master_mp3: Path):
    """Aplica masterización de broadcast con FFmpeg (EBU R128 a -16 LUFS + ecualización y compresión)."""
    print(f"[*] Masterizando audio con FFmpeg (Estándar broadcast EBU R128: -16 LUFS)...")
    
    audio_filter = (
        "equalizer=f=120:width_type=o:w=1:g=-3,"
        "equalizer=f=3000:width_type=o:w=1.2:g=2.5,"
        "compand=attacks=0.02:decays=0.15:points=-60/-60|-30/-16|-12/-6|0/-2:gain=2,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,"
        "afade=t=in:ss=0:d=0.3"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(in_file),
        "-af", audio_filter,
        "-b:a", "192k",
        "-ar", "48000",
        str(out_master_mp3)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and out_master_mp3.exists():
        sz = out_master_mp3.stat().st_size // 1024
        print(f"  [✓] Master broadcast generado: {out_master_mp3.name} ({sz} KB)")
    else:
        print(f"  [-] Error en FFmpeg: {res.stderr}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Generador de podcast de investigación para Última Prensa")
    parser.add_argument("--guion", required=True, help="Ruta al archivo Markdown del guión de locución")
    parser.add_argument("--backend", default="kokoro", choices=["kokoro", "edge"], help="Motor TTS (kokoro o edge)")
    parser.add_argument("--voz", default="em_alex", help="Voz (kokoro: em_alex, ef_dora; edge: es-ES-AlvaroNeural, es-CL-CatalinaNeural)")
    parser.add_argument("--velocidad", default="-2%", help="Ajuste de velocidad para Edge TTS")
    parser.add_argument("--salida", required=True, help="Ruta de destino del archivo MP3 masterizado")
    parser.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR), help="Directorio con pesos de Kokoro ONNX")

    args = parser.parse_args()
    guion_path = Path(args.guion).resolve()
    if not guion_path.exists():
        print(f"[-] Error: Guión no encontrado: {guion_path}", file=sys.stderr)
        sys.exit(1)

    out_final = Path(args.salida).resolve()
    out_dir = out_final.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    texto = extraer_texto_locucion(guion_path)
    palabras = len(texto.split())
    print(f"============================================================")
    print(f"Producción de Podcast de Investigación // Última Prensa")
    print(f"============================================================")
    print(f"Guión:       {guion_path.name} ({palabras} palabras)")
    print(f"Backend:     {args.backend}")
    print(f"Voz:         {args.voz}")
    print(f"Salida:      {out_final.name}")
    print(f"------------------------------------------------------------")

    temp_raw = out_dir / f"temp_raw_{args.backend}.wav"
    temp_srt = out_dir / (out_final.stem + ".srt")

    if args.backend == "kokoro":
        sintetizar_con_kokoro(texto, args.voz, temp_raw, Path(args.model_dir))
        masterizar_audio(temp_raw, out_final)
    else:
        temp_mp3 = out_dir / "temp_raw_edge.mp3"
        asyncio.run(sintetizar_con_edge(texto, args.voz, args.velocidad, temp_mp3, temp_srt))
        masterizar_audio(temp_mp3, out_final)
        if temp_mp3.exists():
            temp_mp3.unlink()

    if temp_raw.exists():
        temp_raw.unlink()

    # Verificar duración final con ffprobe
    res = subprocess.run([
        "ffprobe", "-i", str(out_final),
        "-show_entries", "format=duration",
        "-v", "quiet", "-of", "csv=p=0"
    ], capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        dur_s = float(res.stdout.strip())
        minutos = int(dur_s // 60)
        segundos = int(dur_s % 60)
        print(f"\n[✓] Duración final exacta: {minutos:02d}:{segundos:02d} min ({dur_s:.1f} s)")

if __name__ == "__main__":
    main()
