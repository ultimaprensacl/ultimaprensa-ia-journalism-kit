#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector y Auditor de Redundancia Léxica y Cohesión Referencial para Última Prensa.
Herramienta de estilo editorial y economía léxica.

Analiza textos periodísticos para identificar:
1. Repetición de entidades o nombres propios en ventanas cortas de proximidad (efecto martilleo).
2. Densidad léxica desproporcionada de sustantivos y conceptos clave.
3. Sugerencias automáticas de sustitución correferencial (hiperónimos, perífrasis,
   pronombres, elipsis o títulos institucionales) conforme al manual de estilo.
"""

import sys
import os
import re
from typing import List, Dict, Tuple, Any
from collections import Counter, defaultdict

# Diccionario de correferentes periodísticos recomendados (contexto público e investigación)
CORREFERENTES_SUGERIDOS = {
    "muriel muñoz": [
        "la directora del DESAM",
        "la jefa comunal de salud",
        "la titular del departamento",
        "la máxima autoridad técnica comunal",
        "Muñoz Moreno",
        "la jefa del servicio",
        "la autoridad edilicia"
    ],
    "alejandro schulze": [
        "el exdirector subrogante",
        "el médico de familia",
        "el líder de Aprosam",
        "el otrora jefe de Gestión en Salud",
        "el facultativo",
        "el dirigente gremial",
        "Schulze Barrientos"
    ],
    "schulze": [
        "el exdirector subrogante",
        "el facultativo",
        "el dirigente gremial",
        "el otrora jefe de gestión",
        "el médico"
    ],
    "circular n.° 62": [
        "el instructivo comunal",
        "la resolución de marras",
        "el documento de nueve páginas",
        "la disposición administrativa",
        "la orden interna"
    ],
    "circular": [
        "el instructivo",
        "el documento",
        "la resolución",
        "la disposición",
        "la orden"
    ],
    "minuta": [
        "el texto reservado",
        "el instructivo",
        "el documento de trabajo",
        "la pauta oficial",
        "el escrito"
    ],
    "sapu": [
        "los recintos de urgencia barrial",
        "los dispositivos de atención primaria",
        "las postas de urgencia",
        "los centros asistenciales comunales",
        "las urgencias periféricas"
    ],
    "desam": [
        "el departamento de salud municipal",
        "la dirección técnica comunal",
        "el servicio municipalizado",
        "la entidad de salud primaria"
    ],
    "auditoría": [
        "el informe de control interno",
        "el expediente de fiscalización",
        "la indagatoria contable",
        "la inspección técnica",
        "el documento contralor"
    ],
    "pileta": [
        "la fuente ornamental",
        "la estructura hídrica",
        "la atracción acuática",
        "la obra de la Plaza de Armas",
        "el proyecto ornamental"
    ],
    "municipio": [
        "la administración comunal",
        "la casa consistorial",
        "la corporación edilicia",
        "el gobierno local"
    ]
}

# Palabras vacías en español que no constituyen redundancia estilística
PALABRAS_VACIAS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "al",
    "en", "por", "para", "con", "sin", "sobre", "tras", "durante", "mediante",
    "y", "e", "o", "u", "ni", "que", "se", "su", "sus", "como", "mas", "pero",
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquel", "aquella",
    "es", "son", "fue", "fueron", "era", "eran", "ser", "ha", "han", "había",
    "no", "si", "ya", "le", "les", "lo", "me", "nos", "te", "muy", "más", "menos"
}


class DetectorRedundancia:
    """Motor de análisis de redundancia léxica y distancia referencial."""

    def __init__(self, ventana_proximidad: int = 60):
        self.ventana = ventana_proximidad

    def limpiar_texto(self, markdown_text: str) -> str:
        """Remueve tablas, bloques de código y enlaces markdown para analizar prosa pura."""
        t = re.sub(r'```.*?```', '', markdown_text, flags=re.DOTALL)
        t = re.sub(r'\|.*?\|', ' ', t)
        t = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', t)
        t = re.sub(r'[#>*_`]', ' ', t)
        return t

    def analizar_parrafos(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Analiza cada párrafo buscando concentración de términos repetidos."""
        parrafos = [p.strip() for p in markdown_text.split("\n\n") if p.strip()]
        reporte_parrafos = []

        for num_p, p in enumerate(parrafos, 1):
            if p.startswith("#") or p.startswith("|") or len(p) < 40:
                continue
            
            palabras = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{4,}\b', p.lower())
            significativas = [w for w in palabras if w not in PALABRAS_VACIAS]
            conteo = Counter(significativas)

            repetidas = {k: v for k, v in conteo.items() if v >= 3}
            if repetidas:
                reporte_parrafos.append({
                    "parrafo": num_p,
                    "fragmento": p[:120] + "...",
                    "repeticiones": repetidas
                })

        return reporte_parrafos

    def analizar_proximidad(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Detecta repeticiones de la misma entidad o término dentro de una ventana corta de palabras."""
        texto_limpio = self.limpiar_texto(markdown_text)
        palabras_con_pos = [
            (m.group(0), m.start(), m.end())
            for m in re.finditer(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{3,}\b', texto_limpio)
        ]

        alertas_proximidad = []
        historial_pos = defaultdict(list)

        for idx, (palabra, start, end) in enumerate(palabras_con_pos):
            palabra_norm = palabra.lower()
            if palabra_norm in PALABRAS_VACIAS:
                continue

            # Revisamos si coincide con términos monitoreados o palabras clave
            if palabra_norm in historial_pos:
                ultimas_pos = historial_pos[palabra_norm]
                if ultimas_pos:
                    distancia_palabras = idx - ultimas_pos[-1]
                    if distancia_palabras < self.ventana:
                        alertas_proximidad.append({
                            "palabra": palabra,
                            "distancia": distancia_palabras,
                            "indice_aparicion": idx,
                            "sugerencia": CORREFERENTES_SUGERIDOS.get(palabra_norm, [])
                        })
            historial_pos[palabra_norm].append(idx)

        return alertas_proximidad

    def generar_diagnostico(self, markdown_text: str) -> Dict[str, Any]:
        """Genera un diagnóstico global consolidado de economía léxica."""
        # Conteo de entidades monitoreadas
        conteos_entidades = {}
        for ent, sugerencias in CORREFERENTES_SUGERIDOS.items():
            patron = rf'\b{re.escape(ent)}\b'
            coincidencias = len(re.findall(patron, markdown_text, re.IGNORECASE))
            if coincidencias > 0:
                conteos_entidades[ent] = {
                    "total": coincidencias,
                    "sugerencias": sugerencias
                }

        alertas_prox = self.analizar_proximidad(markdown_text)
        parrafos_saturados = self.analizar_parrafos(markdown_text)

        return {
            "entidades": conteos_entidades,
            "proximidad_critica": [a for a in alertas_prox if a["distancia"] <= 25],
            "parrafos_saturados": parrafos_saturados
        }


def main():
    if len(sys.argv) < 2:
        print("Uso: python detector_redundancia_lexica.py <archivo.md> [--ventana N]")
        sys.exit(1)

    archivo = sys.argv[1]
    ventana = 30
    if "--ventana" in sys.argv:
        v_idx = sys.argv.index("--ventana") + 1
        if v_idx < len(sys.argv):
            ventana = int(sys.argv[v_idx])

    if not os.path.exists(archivo):
        print(f"Error: No se encontró el archivo {archivo}")
        sys.exit(1)

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    detector = DetectorRedundancia(ventana_proximidad=ventana)
    diagnostico = detector.generar_diagnostico(contenido)

    print("=" * 65)
    print(f"ANÁLISIS DE REDUNDANCIA Y COHESIÓN REFERENCIAL: {os.path.basename(archivo)}")
    print("=" * 65)

    print("\n1. FRECUENCIA DE ENTIDADES Y CONCEPTOS CLAVE:")
    print("-" * 65)
    for ent, data in sorted(diagnostico["entidades"].items(), key=lambda x: x[1]["total"], reverse=True):
        alerta = "⚠️ [EXCESIVO]" if data["total"] >= 10 else "ℹ️"
        print(f"{alerta} «{ent.upper()}»: {data['total']} apariciones")
        if data["total"] >= 6:
            sugs = ", ".join(data["sugerencias"][:3])
            print(f"    Sugerencias de variación: {sugs}")

    print("\n2. ALERTAS DE CERCANÍA INMEDIATA (Distancia < 25 palabras):")
    print("-" * 65)
    if not diagnostico["proximidad_critica"]:
        print("✓ No se detectaron martilleos o repeticiones a distancia crítica.")
    else:
        for al in diagnostico["proximidad_critica"][:12]:
            sug_txt = f" -> Sugerencia: {al['sugerencia'][0]}" if al['sugerencia'] else ""
            print(f"  • Palabra «{al['palabra']}» repetida tras solo {al['distancia']} palabras{sug_txt}")

    print("\n3. PÁRRAFOS CON ALTA CONCENTRACIÓN DE UN MISMO LEMA:")
    print("-" * 65)
    if not diagnostico["parrafos_saturados"]:
        print("✓ Ningún párrafo supera el límite de 3 repeticiones del mismo término.")
    else:
        for ps in diagnostico["parrafos_saturados"][:5]:
            print(f"  • Párrafo {ps['parrafo']}:")
            for w, c in ps["repeticiones"].items():
                print(f"    - Término «{w}» repetido {c} veces.")
            print(f"    - Fragmento: {ps['fragmento']}\n")

    print("=" * 65)


if __name__ == "__main__":
    main()
