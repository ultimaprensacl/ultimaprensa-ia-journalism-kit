#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transcribir_audio_investigacion.py
---------------------------------
Herramienta de transcripción fonética de alta precisión para periodismo de investigación
basada en faster-whisper (SYSTRAN/faster-whisper, 17k+ estrellas) y CTranslate2.

Características:
- Procesamiento acelerado por CPU multinúcleo con cuantización INT8.
- Conversión y remuestreo automático con FFmpeg a 16 kHz mono.
- Sesgo de vocabulario especializado (initial_prompt) con términos del caso ULagos-Kimün.
- Salida triple: Texto limpio con marcas de tiempo [HH:MM:SS], JSON estructurado y subtítulos SRT.
- Compatible con Python 3.14 y el ecosistema de Última Prensa.
"""

import os
import sys
import argparse
import subprocess
import json
import time
from pathlib import Path
import soundfile as sf
from faster_whisper import WhisperModel

# Vocabulario de contexto predeterminado para el caso ULagos - Kimün
VOCABULARIO_CASO_ULAGOS = (
    "Universidad de Los Lagos, ULagos, rector Óscar Garrido Álvarez, Fundación Kimün, "
    "Corporación Kimün, Jaime Huincahue, Diego Ancalao, Consejo Superior, Junta Directiva, "
    "Lord Cochrane 1039, Patricio Lynch 1346, IP Los Lagos, Instituto Profesional Los Lagos, "
    "CFT Los Lagos, Centro de Formación Técnica Los Lagos, Osorno, Puerto Montt, Castro, "
    "CNA, Comisión Nacional de Acreditación, acreditación institucional, quiebra fraudulenta, "
    "liquidación concursal, 2° Juzgado de Letras de Osorno, Rol C-373-2024, Rol C-2580-2023, "
    "Arturo Droguett, Juan Félix Burotto, Álvaro Poblete, banco Itaú, hipoteca, simulación absoluta."
)

def formatear_tiempo(segundos: float) -> str:
    """Convierte segundos a formato HH:MM:SS."""
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{segs:02d}"

def formatear_tiempo_srt(segundos: float) -> str:
    """Convierte segundos a formato de subtítulo SRT HH:MM:SS,mmm."""
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    milis = int((segundos - int(segundos)) * 1000)
    return f"{horas:02d}:{minutos:02d}:{segs:02d},{milis:03d}"

def preparar_audio_16k(ruta_entrada: Path, ruta_salida_wav: Path) -> bool:
    """Extrae y remuestrea el audio a WAV 16kHz mono usando ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(ruta_entrada),
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(ruta_salida_wav)
    ]
    try:
        resultado = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Error ejecutando FFmpeg: {e.stderr.decode('utf-8', errors='ignore')}", file=sys.stderr)
        return False

def transcribir_audio(
    archivo_audio: str,
    modelo_nombre: str = "small",
    idioma: str = "es",
    prompt_personalizado: str = None,
    carpeta_salida: str = None,
    hilos_cpu: int = 8
):
    ruta_audio = Path(archivo_audio).resolve()
    if not ruta_audio.exists():
        print(f"[!] Error: El archivo {ruta_audio} no existe.", file=sys.stderr)
        sys.exit(1)

    dir_salida = Path(carpeta_salida).resolve() if carpeta_salida else ruta_audio.parent
    dir_salida.mkdir(parents=True, exist_ok=True)
    nombre_base = ruta_audio.stem

    archivo_wav_temp = dir_salida / f"{nombre_base}_16k_temp.wav"
    archivo_txt = dir_salida / f"{nombre_base}_transcripcion_whisper.txt"
    archivo_json = dir_salida / f"{nombre_base}_transcripcion_whisper.json"
    archivo_srt = dir_salida / f"{nombre_base}_transcripcion_whisper.srt"

    print("=" * 70)
    print("🎙️ SISTEMA DE TRANSCRIPCIÓN PERIODÍSTICA DE ALTA PRECISIÓN (FASTER-WHISPER)")
    print("=" * 70)
    print(f"Archivo de entrada:  {ruta_audio.name}")
    print(f"Modelo seleccionado: {modelo_nombre} (Cuantización INT8 en CPU)")
    print(f"Hilos de CPU:        {hilos_cpu}")
    print(f"Directorio salida:   {dir_salida}")
    print("-" * 70)

    # Paso 1: Remuestreo con FFmpeg
    print("[1/3] Normalizando audio a WAV 16 kHz mono con FFmpeg...")
    if not preparar_audio_16k(ruta_audio, archivo_wav_temp):
        sys.exit(1)

    # Paso 2: Cargar datos en memoria con soundfile
    print("[2/3] Cargando audio y modelo Whisper en memoria...")
    audio_data, sample_rate = sf.read(str(archivo_wav_temp), dtype="float32")
    duracion_total = len(audio_data) / sample_rate
    print(f"      Duración total del audio: {formatear_tiempo(duracion_total)} ({duracion_total:.1f} s)")

    t0 = time.time()
    modelo = WhisperModel(
        modelo_nombre,
        device="cpu",
        compute_type="int8",
        cpu_threads=hilos_cpu
    )

    prompt = prompt_personalizado if prompt_personalizado else VOCABULARIO_CASO_ULAGOS

    print(f"[3/3] Iniciando transcripción fonética con sesgo léxico contextual...")
    print(f"      Prompt contextual cargado ({len(prompt.split(','))} términos institucionales).")
    print("-" * 70)

    segmentos_iter, info = modelo.transcribe(
        audio_data,
        language=idioma,
        initial_prompt=prompt,
        beam_size=5,
        vad_filter=True, # Filtro de actividad de voz para ignorar silencios largos
        vad_parameters=dict(min_silence_duration_ms=500)
    )

    registros_segmentos = []
    lineas_txt = []
    lineas_srt = []

    indice = 1
    ultimo_tiempo_notificado = 0

    with open(archivo_txt, "w", encoding="utf-8") as f_txt:
        f_txt.write(f"# TRANSCRIPCIÓN PERIODÍSTICA: {ruta_audio.name}\n")
        f_txt.write(f"# Duración: {formatear_tiempo(duracion_total)}\n")
        f_txt.write(f"# Modelo: {modelo_nombre} (faster-whisper)\n")
        f_txt.write(f"# Fecha de procesamiento: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for s in segmentos_iter:
            tiempo_inicio = formatear_tiempo(s.start)
            tiempo_fin = formatear_tiempo(s.end)
            texto_limpio = s.text.strip()

            linea_narrativa = f"[{tiempo_inicio} -> {tiempo_fin}] {texto_limpio}\n"
            f_txt.write(linea_narrativa)
            f_txt.flush()

            # Guardar en registros para JSON
            registros_segmentos.append({
                "id": indice,
                "inicio_seg": round(s.start, 2),
                "fin_seg": round(s.end, 2),
                "tiempo_inicio": tiempo_inicio,
                "tiempo_fin": tiempo_fin,
                "texto": texto_limpio,
                "avg_logprob": round(s.avg_logprob, 3),
                "no_speech_prob": round(s.no_speech_prob, 3)
            })

            # Subtítulo SRT
            srt_inicio = formatear_tiempo_srt(s.start)
            srt_fin = formatear_tiempo_srt(s.end)
            lineas_srt.append(f"{indice}\n{srt_inicio} --> {srt_fin}\n{texto_limpio}\n\n")

            # Progreso en consola cada ~60 segundos de audio
            if s.end - ultimo_tiempo_notificado >= 60:
                progreso_pct = min(100.0, (s.end / duracion_total) * 100)
                tiempo_transcurrido = time.time() - t0
                print(f"[{tiempo_inicio} / {formatear_tiempo(duracion_total)}] ({progreso_pct:.1f}%) -> {texto_limpio[:75]}...")
                ultimo_tiempo_notificado = s.end

            indice += 1

    # Guardar JSON
    with open(archivo_json, "w", encoding="utf-8") as f_json:
        json.dump({
            "archivo": ruta_audio.name,
            "duracion_seg": round(duracion_total, 2),
            "duracion_formato": formatear_tiempo(duracion_total),
            "modelo": modelo_nombre,
            "idioma_detectado": info.language,
            "probabilidad_idioma": round(info.language_probability, 3),
            "total_segmentos": len(registros_segmentos),
            "segmentos": registros_segmentos
        }, f_json, ensure_ascii=False, indent=2)

    # Guardar SRT
    with open(archivo_srt, "w", encoding="utf-8") as f_srt:
        f_srt.writelines(lineas_srt)

    # Limpiar archivo temporal WAV
    if archivo_wav_temp.exists():
        archivo_wav_temp.unlink()

    tiempo_total = time.time() - t0
    factor_velocidad = duracion_total / tiempo_total if tiempo_total > 0 else 0

    print("=" * 70)
    print("✅ TRANSCRIPCIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print(f"Tiempo de ejecución:  {formatear_tiempo(tiempo_total)} ({tiempo_total:.1f} segundos)")
    print(f"Velocidad de proceso: {factor_velocidad:.1f}x tiempo real")
    print(f"Total de segmentos:   {len(registros_segmentos)}")
    print(f"Archivos generados:")
    print(f"  • Texto formateado: {archivo_txt}")
    print(f"  • JSON estructurado: {archivo_json}")
    print(f"  • Subtítulos SRT:   {archivo_srt}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Transcriptor de audio para periodismo de investigación")
    parser.add_argument("audio", help="Ruta al archivo de audio (MP3, WAV, M4A, OGG)")
    parser.add_argument("--modelo", "-m", default="small", choices=["tiny", "base", "small", "medium", "large-v3-turbo"], help="Tamaño del modelo Whisper (def: small)")
    parser.add_argument("--idioma", "-l", default="es", help="Código de idioma (def: es)")
    parser.add_argument("--prompt", "-p", default=None, help="Prompt contextual de nombres y términos")
    parser.add_argument("--salida", "-o", default=None, help="Directorio de destino")
    parser.add_argument("--hilos", "-t", type=int, default=8, help="Número de hilos de CPU (def: 8)")

    args = parser.parse_args()
    transcribir_audio(
        archivo_audio=args.audio,
        modelo_nombre=args.modelo,
        idioma=args.idioma,
        prompt_personalizado=args.prompt,
        carpeta_salida=args.salida,
        hilos_cpu=args.hilos
    )

if __name__ == "__main__":
    main()
