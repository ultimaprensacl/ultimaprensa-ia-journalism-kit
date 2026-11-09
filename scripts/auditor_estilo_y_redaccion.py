#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auditor_estilo_y_redaccion.py — Auditor de Ritmo Narrativo, Legibilidad y Sentido para Última Prensa.

Inspirado en la doctrina del Investigative Journalism Manual (KAS, Capítulo 8),
las adaptaciones de legibilidad para el español de Flesch-Szigriszt y Fernández-Huerta (textstat),
y la estilística periodística de alta intensidad.

Capacidades:
1. Análisis de Ritmo y Variación de Longitud de Oraciones (The Music of Prose / Gary Provost).
2. Detección y localización exacta de oraciones sofocantes (> 45 palabras) con sugerencias de corte.
3. Índices científicos de legibilidad para español (Szigriszt-Pazos, Fernández-Huerta, Gutiérrez de Polini).
4. Detección de Estilo Nominal y Prosa Burocrática (exceso de sufijos -ción, -miento, -dad, -ncia).
5. Detección de Voz Pasiva Perifrástica (sustituir por voz activa con sujeto responsable).
6. Salud y dimensión de párrafos (control de bloques mastodónticos > 120 palabras para lectura digital).
7. Mapeo de Conectores Lógicos y Sentido Narrativo (causa, contraste, consecuencia y secuencia temporal).
"""

import os
import re
import sys
import statistics
from typing import Any, Dict, List, Tuple
from collections import Counter

# Intentar cargar textstat para métricas estándar en español
try:
    import textstat
    textstat.set_lang("es")
    TEXTSTAT_DISPONIBLE = True
except Exception:
    TEXTSTAT_DISPONIBLE = False

# Sufijos clásicos de nominalización en español que fosilizan la prosa activa
SUFIJOS_NOMINALIZACION = (
    "ción", "ciones", "sión", "siones", "miento", "mientos",
    "ancia", "ancias", "encia", "encias", "bilidad", "bilidades"
)

# Patrones de pasiva perifrástica con complemento agente
PATRONES_PASIVA = [
    r"\b(?:fue|fueron|era|eran|ha sido|han sido|había sido|habían sido|será|serán)\s+([a-záéíóúñ]+(?:ado|ada|ados|adas|ido|ida|idos|idas|to|ta|tos|tas|so|sa|sos|sas|cho|cha|chos|chas))\s+(?:por|de parte de)\b",
]

# Conectores discursivos clasificados por función lógica
CONECTORES_LOGICOS = {
    "contraste": [
        "sin embargo", "no obstante", "en contraste", "a diferencia de", "pese a",
        "a pesar de", "por el contrario", "mientras que", "en cambio", "empero"
    ],
    "causa": [
        "debido a", "a causa de", "producto de", "puesto que", "ya que",
        "dado que", "en razón de", "a raíz de", "gracias a"
    ],
    "consecuencia": [
        "por lo tanto", "en consecuencia", "por consiguiente", "de este modo",
        "así", "de ahí que", "por ello", "de tal forma"
    ],
    "tiempo_secuencia": [
        "posteriormente", "luego", "tras", "meses después", "semanas más tarde",
        "al mismo tiempo", "en paralelo", "simultáneamente", "en tanto"
    ]
}


class AuditorEstiloRedaccion:
    """Motor de análisis de calidad sintáctica, ritmo y sentido periodístico."""

    def __init__(self, umbral_oracion_larga: int = 40, umbral_parrafo_largo: int = 120):
        self.umbral_oracion_larga = umbral_oracion_larga
        self.umbral_parrafo_largo = umbral_parrafo_largo

    def extraer_prosa_limpia(self, markdown_text: str) -> str:
        """Remueve fuentes, tablas, enlaces, encabezados y código para aislar la prosa de lectura."""
        # Cortar en Fuentes documentales
        partes = re.split(
            r"^#{2,3}\s+(?:\d+\.\s*)?(?:Fuentes documentales|Base de referencias|Obras citadas|Referencias)",
            markdown_text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        prosa = partes[0]
        # Quitar bloques de código
        prosa = re.sub(r"```.*?```", " ", prosa, flags=re.DOTALL)
        # Quitar tablas markdown
        prosa = re.sub(r"^\s*\|.*\|\s*$", " ", prosa, flags=re.MULTILINE)
        # Quitar imágenes markdown primero (antes de procesar enlaces)
        prosa = re.sub(r"!\[.*?\]\(.*?\)", " ", prosa, flags=re.DOTALL)
        # Quitar epígrafes o pies de figura inmediatamente posteriores a imágenes
        prosa = re.sub(r"^\s*\*([^*]+)\*\s*$", r" \1 ", prosa, flags=re.MULTILINE)
        # Convertir enlaces a su texto visible
        prosa = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", prosa)
        # Quitar URLs planas
        prosa = re.sub(r"https?://\S+", " ", prosa)
        # Quitar encabezados
        prosa = re.sub(r"^#{1,6}\s+.*$", " ", prosa, flags=re.MULTILINE)
        # Quitar marcas de formato
        prosa = re.sub(r"[*_`>]", " ", prosa)
        return prosa

    def segmentar_oraciones(self, texto_limpio: str) -> List[Dict[str, Any]]:
        """Segmenta oraciones considerando abreviaturas y puntuación del español."""
        # Proteger abreviaturas comunes para no romper oraciones en falsos puntos
        t = re.sub(r"\b(N\.°|N°|Art\.|Inc\.|D\.L\.|S\.A\.|E\.I\.R\.L\.|SpA\.|EE\. UU\.|Gral\.|Sr\.|Sra\.|Dr\.|Dra\.)\s*", lambda m: m.group(0).replace(".", "@@"), texto_limpio)
        raw_oraciones = re.split(r"(?<=[\.\?!])\s+", t)

        oraciones = []
        for o in raw_oraciones:
            restaurada = o.replace("@@", ".").strip()
            # Limpiar espacios múltiples
            restaurada = re.sub(r"\s+", " ", restaurada)
            palabras = [w for w in re.findall(r"\b[\w\-]+\b", restaurada) if not w.isdigit()]
            num_palabras = len(palabras)
            if num_palabras >= 3:
                tipo = "corta" if num_palabras <= 15 else ("media" if num_palabras <= 30 else ("larga" if num_palabras <= self.umbral_oracion_larga else "sofocante"))
                oraciones.append({
                    "texto": restaurada,
                    "num_palabras": num_palabras,
                    "tipo": tipo
                })
        return oraciones

    def analizar_ritmo(self, oraciones: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evalúa la variación musical y dinámica de la prosa (Doctrina KAS Cap. 8)."""
        if not oraciones:
            return {}

        longitudes = [o["num_palabras"] for o in oraciones]
        promedio = statistics.mean(longitudes)
        desviacion = statistics.stdev(longitudes) if len(longitudes) > 1 else 0.0

        conteo_tipos = Counter(o["tipo"] for o in oraciones)
        total = len(oraciones)

        # Detectar rachas monótonas: 3 o más oraciones largas/sofocantes seguidas sin respiro
        rachas_densas = 0
        racha_actual = 0
        for o in oraciones:
            if o["tipo"] in ("larga", "sofocante"):
                racha_actual += 1
                if racha_actual == 3:
                    rachas_densas += 1
            else:
                racha_actual = 0

        # Diagnóstico de ritmo
        if desviacion >= 18.0 and conteo_tipos.get("corta", 0) / total >= 0.15:
            diag_ritmo = "Excelente variación rítmica (alternancia armónica de oraciones cortas y de desarrollo)."
        elif promedio > 38.0:
            diag_ritmo = "Ritmo pesado / fatigoso: predominio excesivo de oraciones subordinadas largas."
        elif desviacion < 10.0:
            diag_ritmo = "Ritmo monótono: las oraciones tienen casi la misma longitud sin contraste."
        else:
            diag_ritmo = "Ritmo moderado: cumple estándares periodísticos con margen de mayor dinamismo."

        return {
            "total_oraciones": total,
            "longitud_promedio_palabras": round(promedio, 1),
            "desviacion_estandar_ritmo": round(desviacion, 1),
            "oracion_mas_corta": min(longitudes),
            "oracion_mas_larga": max(longitudes),
            "distribucion": {
                "cortas_impacto_lt_16": conteo_tipos.get("corta", 0),
                "medias_desarrollo_16_30": conteo_tipos.get("media", 0),
                "largas_complejas_31_40": conteo_tipos.get("larga", 0),
                "sofocantes_gt_40": conteo_tipos.get("sofocante", 0),
            },
            "porcentaje_sofocantes": round((conteo_tipos.get("sofocante", 0) / total) * 100.0, 1),
            "rachas_fatigosas_detectadas": rachas_densas,
            "diagnostico_ritmo": diag_ritmo
        }

    def calcular_legibilidad_es(self, texto_limpio: str) -> Dict[str, Any]:
        """Calcula los índices de legibilidad científica para el español."""
        if not TEXTSTAT_DISPONIBLE:
            return {"error": "textstat no disponible"}

        sz = textstat.szigriszt_pazos(texto_limpio)
        fh = textstat.fernandez_huerta(texto_limpio)
        gp = textstat.gutierrez_polini(texto_limpio)

        # Escala cualitativa oficial de Szigriszt-Pazos / Barrio-Cantalejo (Inflesz)
        if sz >= 80:
            escala = "Muy fácil (Lectura infantil / primaria)"
        elif sz >= 70:
            escala = "Bastante fácil (Divulgación ágil)"
        elif sz >= 60:
            escala = "Estándar / Adecuada (Prensa y periodismo de calidad - Nivel Óptimo)"
        elif sz >= 50:
            escala = "Algo difícil (Requiere concentración / universitario)"
        elif sz >= 40:
            escala = "Difícil (Estilo técnico / académico denso)"
        else:
            escala = "Muy oscura / Burocrática (Ininteligible para el público general)"

        return {
            "szigriszt_pazos": round(sz, 2),
            "fernandez_huerta": round(fh, 2),
            "gutierrez_polini": round(gp, 2),
            "nivel_inflesz": escala
        }

    def analizar_nominalizaciones(self, texto_limpio: str) -> Dict[str, Any]:
        """Detecta el vicio de la prosa burocrática mediante sustantivos abstractos fosilizados."""
        palabras = re.findall(r"\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{5,}\b", texto_limpio.lower())
        total_palabras = len(palabras)
        if total_palabras == 0:
            return {"total_nominalizaciones": 0, "porcentaje": 0.0, "mas_frecuentes": []}

        noms = [w for w in palabras if w.endswith(SUFIJOS_NOMINALIZACION)]
        conteo = Counter(noms)
        pct = (len(noms) / total_palabras) * 100.0

        alerta_burocracia = pct >= 6.5

        return {
            "total_nominalizaciones": len(noms),
            "porcentaje_sobre_vocabulario": round(pct, 2),
            "alerta_prosa_burocratica": alerta_burocracia,
            "mas_frecuentes": conteo.most_common(8),
            "recomendacion": "Reemplazar construcciones nominales por verbos de acción ('se entregó' en vez de 'se procedió a la entrega')." if alerta_burocracia else "Nivel saludable de verbosidad activa."
        }

    def analizar_voz_pasiva(self, texto_limpio: str) -> List[Dict[str, Any]]:
        """Identifica oraciones en pasiva perifrástica pesada."""
        alertas = []
        for pat in PATRONES_PASIVA:
            for m in re.finditer(pat, texto_limpio, flags=re.IGNORECASE):
                start = max(0, m.start() - 30)
                end = min(len(texto_limpio), m.end() + 30)
                ctx = texto_limpio[start:end].strip().replace("\n", " ")
                alertas.append({
                    "construccion_pasiva": m.group(0),
                    "participio": m.group(1),
                    "contexto": f"...{ctx}...",
                    "sugerencia": "Reestructurar a voz activa identificando al sujeto directo que realiza la acción."
                })
        return alertas

    def analizar_parrafos(self, markdown_text: str) -> Dict[str, Any]:
        """Evalúa la extensión de los párrafos para consumo digital y móvil."""
        partes = re.split(
            r"^#{2,3}\s+(?:\d+\.\s*)?(?:Fuentes documentales|Base de referencias|Obras citadas|Referencias)",
            markdown_text,
            flags=re.IGNORECASE | re.MULTILINE,
        )[0]
        bloques = [
            p.strip()
            for p in re.split(r"\n\s*\n", partes)
            if p.strip() and not p.strip().startswith(("#", "|", "!", ">"))
        ]

        parrafos_largos = []
        parrafos_cortos = []
        for idx, p in enumerate(bloques, 1):
            num_w = len(re.findall(r"\b[\w\-]+\b", p))
            if num_w >= self.umbral_parrafo_largo:
                parrafos_largos.append({
                    "numero": idx,
                    "palabras": num_w,
                    "fragmento": p[:120].replace("\n", " ") + "...",
                    "alerta": f"Párrafo de {num_w} palabras supera el umbral digital ({self.umbral_parrafo_largo} palabras). Conviene dividirlo en dos mini-historias."
                })
            elif num_w < 15 and num_w >= 3:
                parrafos_cortos.append({
                    "numero": idx,
                    "palabras": num_w,
                    "fragmento": p[:90].replace("\n", " ") + "..."
                })

        return {
            "total_parrafos_prosa": len(bloques),
            "parrafos_mastodonticos": parrafos_largos,
            "parrafos_de_impacto_cortos": parrafos_cortos,
        }

    def mapear_conectores_narrativos(self, texto_limpio: str) -> Dict[str, Any]:
        """Calcula la presencia y variedad de hilos lógicos en la narración."""
        t_low = texto_limpio.lower()
        mapa = {}
        total_conectores = 0
        for categoria, frases in CONECTORES_LOGICOS.items():
            encontrados = []
            for f in frases:
                cnt = len(re.findall(rf"\b{re.escape(f)}\b", t_low))
                if cnt > 0:
                    encontrados.append((f, cnt))
                    total_conectores += cnt
            mapa[categoria] = encontrados

        return {
            "total_conectores_logicos": total_conectores,
            "por_categoria": mapa,
            "diagnostico": "Equilibrio narrativo adecuado en la transición de ideas." if total_conectores >= 10 else "Escasez de conectores explícitos: riesgo de yuxtaposición o saltos temáticos abruptos."
        }

    def analizar_ruido_tecnico(self, markdown_text: str) -> Dict[str, Any]:
        """Detecta RUTs, códigos alfanuméricos tipo CVE, hashes y nombres legales cuádruples en la prosa narrativa."""
        partes = re.split(
            r"^#{2,3}\s+(?:\d+\.\s*)?(?:Fuentes documentales|Base de referencias|Obras citadas|Referencias)",
            markdown_text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        prosa_cuerpo = partes[0]
        # Quitar bloques de código
        prosa_cuerpo = re.sub(r"```.*?```", " ", prosa_cuerpo, flags=re.DOTALL)

        # 1. Detección de RUTs / RUNs en el cuerpo
        patron_rut = r"\b\d{1,2}\.\d{3}\.\d{3}-[\dkK]\b|\b\d{7,8}-[\dkK]\b"
        ruts_encontrados = re.findall(patron_rut, prosa_cuerpo)

        # 2. Detección de CVEs en el cuerpo
        patron_cve = r"\bCVE\s+[`\"']?[A-Za-z0-9_-]+[`\"']?|\bCR[a-zA-Z0-9]{8,12}\b"
        cves_encontrados = re.findall(patron_cve, prosa_cuerpo)

        # 3. Detección de backticks con códigos administrativos (FA-XXXX, ACXXXX, etc.)
        patron_backticks = r"`(?:FA-\d+|AC[a-zA-Z0-9]+|\d{7,8})`"
        backticks_encontrados = re.findall(patron_backticks, prosa_cuerpo)

        # 4. Detección de nombres cuádruples legales (Nombre + Segundo Nombre + Apellido + Segundo Apellido)
        patron_nombre_cuadruple = r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\b"
        excepciones_inst = ["Ministerio de Economía", "Servicio de Impuestos", "Registro de Empresas", "Consejo para la Transparencia", "Registro Central de Colaboradores"]
        nombres_cuadruples = []
        for m in re.finditer(patron_nombre_cuadruple, prosa_cuerpo):
            full = m.group(0)
            if not any(exc in full for exc in excepciones_inst):
                nombres_cuadruples.append(full)

        return {
            "total_ruts": len(ruts_encontrados),
            "ruts_detectados": ruts_encontrados,
            "total_cves": len(cves_encontrados),
            "cves_detectados": cves_encontrados,
            "total_backticks_tecnicos": len(backticks_encontrados),
            "backticks_detectados": backticks_encontrados,
            "total_nombres_cuadruples": len(nombres_cuadruples),
            "nombres_cuadruples": list(set(nombres_cuadruples)),
            "es_limpio": len(ruts_encontrados) == 0 and len(cves_encontrados) == 0 and len(backticks_encontrados) == 0 and len(nombres_cuadruples) == 0
        }

    def generar_auditoria_completa(self, markdown_text: str) -> Dict[str, Any]:
        """Ejecuta todos los módulos de redacción, ritmo y sentido."""
        prosa_limpia = self.extraer_prosa_limpia(markdown_text)
        oraciones = self.segmentar_oraciones(prosa_limpia)

        ritmo = self.analizar_ritmo(oraciones)
        legibilidad = self.calcular_legibilidad_es(prosa_limpia)
        nominalizacion = self.analizar_nominalizaciones(prosa_limpia)
        pasiva = self.analizar_voz_pasiva(prosa_limpia)
        parrafos = self.analizar_parrafos(markdown_text)
        conectores = self.mapear_conectores_narrativos(prosa_limpia)
        ruido = self.analizar_ruido_tecnico(markdown_text)

        # Extraer oraciones sofocantes con su índice
        sofocantes = [o for o in oraciones if o["tipo"] == "sofocante"]

        return {
            "ritmo": ritmo,
            "legibilidad": legibilidad,
            "nominalizacion": nominalizacion,
            "voz_pasiva": pasiva,
            "parrafos": parrafos,
            "conectores_narrativos": conectores,
            "ruido_tecnico": ruido,
            "oraciones_sofocantes": sofocantes
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Auditor de Calidad de Redacción, Ritmo Narrativo y Sentido Periodístico (KAS Cap. 8 / Flesch-Szigriszt)."
    )
    parser.add_argument("archivo", help="Ruta al archivo Markdown del reportaje a auditar.")
    parser.add_argument("--sugerir-cortes", action="store_true", help="Muestra las oraciones sofocantes (> 40 palabras) con posibles puntos de escisión.")

    args = parser.parse_args()

    if not os.path.exists(args.archivo):
        print(f"Error: No se encontró el archivo {args.archivo}")
        sys.exit(1)

    with open(args.archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    auditor = AuditorEstiloRedaccion()
    aud = auditor.generar_auditoria_completa(contenido)

    print("=" * 72)
    print(f"AUDITORÍA DE REDACCIÓN, RITMO Y SENTIDO: {os.path.basename(args.archivo)}")
    print("=" * 72)

    # 1. Ritmo y Música de la Prosa
    r = aud["ritmo"]
    print("\n1. RITMO Y MÚSICA DE LA PROSA (Doctrina KAS Cap. 8):")
    print("-" * 72)
    print(f"  • Total de oraciones analizadas:     {r.get('total_oraciones')}")
    print(f"  • Longitud promedio:                 {r.get('longitud_promedio_palabras')} palabras por oración")
    print(f"  • Variabilidad / Dinámica rítmica:   {r.get('desviacion_estandar_ritmo')} (Desv. estándar)")
    print(f"  • Oración más corta / más larga:     {r.get('oracion_mas_corta')} / {r.get('oracion_mas_larga')} palabras")
    print(f"  • Distribución armónica:")
    dist = r.get("distribucion", {})
    print(f"    - Oraciones cortas de impacto  (<= 15 palabras): {dist.get('cortas_impacto_lt_16', 0)}")
    print(f"    - Oraciones medias desarrollo  (16-30 palabras): {dist.get('medias_desarrollo_16_30', 0)}")
    print(f"    - Oraciones largas complejas   (31-40 palabras): {dist.get('largas_complejas_31_40', 0)}")
    print(f"    - Oraciones sofocantes / densas (> 40 palabras): {dist.get('sofocantes_gt_40', 0)} ({r.get('porcentaje_sofocantes')} %)")
    print(f"  • Diagnóstico rítmico: {r.get('diagnostico_ritmo')}")
    if r.get("rachas_fatigosas_detectadas", 0) > 0:
        print(f"  ⚠️ Alerta: Se detectaron {r.get('rachas_fatigosas_detectadas')} rachas de 3+ oraciones largas seguidas sin pausas de impacto.")

    # 2. Legibilidad Científica en Español
    leg = aud["legibilidad"]
    print("\n2. ÍNDICES CIENTÍFICOS DE LEGIBILIDAD (Flesch adaptado a español):")
    print("-" * 72)
    if "error" not in leg:
        print(f"  • Índice de Szigriszt-Pazos:     {leg['szigriszt_pazos']} puntos (Ideal periodístico: 60 - 75)")
        print(f"  • Índice de Fernández-Huerta:    {leg['fernandez_huerta']} puntos")
        print(f"  • Índice de Gutiérrez de Polini: {leg['gutierrez_polini']} puntos")
        print(f"  • Nivel de Perspicuidad (Inflesz): {leg['nivel_inflesz']}")
    else:
        print("  ⚠️ textstat no disponible para calcular fórmulas de legibilidad.")

    # 3. Control de Prosa Burocrática (Nominalizaciones)
    nom = aud["nominalizacion"]
    print("\n3. ESTILO NOMINAL VS. VERBOS ACTIVOS:")
    print("-" * 72)
    print(f"  • Total de nominalizaciones (-ción, -miento, etc.): {nom['total_nominalizaciones']} ({nom['porcentaje_sobre_vocabulario']} % del léxico)")
    if nom["alerta_prosa_burocratica"]:
        print("  ⚠️ ALERTA: Densidad nominal alta. La prosa corre riesgo de sonar a informe administrativo.")
    else:
        print("  ✓ Equilibrio adecuado entre verbos activos y sustantivos abstractos.")
    if nom["mas_frecuentes"]:
        frec_txt = ", ".join(f"{w} ({c})" for w, c in nom["mas_frecuentes"][:6])
        print(f"  • Términos más reiterados: {frec_txt}")

    # 4. Voz Pasiva
    pas = aud["voz_pasiva"]
    print("\n4. CONSTRUCCIONES EN VOZ PASIVA:")
    print("-" * 72)
    if not pas:
        print("  ✓ Prosa directa y activa. No se detectaron pasivas perifrásticas pesadas.")
    else:
        print(f"  ℹ️ Se detectaron {len(pas)} construcciones pasivas. Verificar si conviene atribuir el sujeto activo:")
        for p_item in pas[:4]:
            print(f"    • «{p_item['construccion_pasiva']}» en: {p_item['contexto']}")

    # 5. Dimensión de Párrafos
    par = aud["parrafos"]
    print("\n5. ARQUITECTURA DE PÁRRAFOS (Consumo Digital y Móvil):")
    print("-" * 72)
    print(f"  • Total de párrafos de texto: {par['total_parrafos_prosa']}")
    if not par["parrafos_mastodonticos"]:
        print("  ✓ Todos los párrafos respetan la extensión óptima para lectura web (< 120 palabras).")
    else:
        print(f"  ⚠️ Hay {len(par['parrafos_mastodonticos'])} párrafos mastodónticos que conviene fraccionar:")
        for pm in par["parrafos_mastodonticos"][:3]:
            print(f"    - Párrafo {pm['numero']} ({pm['palabras']} palabras): {pm['fragmento']}")

    # 6. Conectores Lógicos y Cohesión
    con = aud["conectores_narrativos"]
    print("\n6. HILOS CONDUCTORES Y CONECTORES LÓGICOS:")
    print("-" * 72)
    print(f"  • Conectores discursivos explícitos: {con['total_conectores_logicos']}")
    for cat, items in con["por_categoria"].items():
        if items:
            lista_txt = ", ".join(f"{f} ({c})" for f, c in items[:4])
            print(f"    - {cat.capitalize()}: {lista_txt}")
    print(f"  • Evaluación de cohesión: {con['diagnostico']}")

    # 7. Muestra de Oraciones Sofocantes
    sofs = aud["oraciones_sofocantes"]
    print("\n7. ORACIONES SOFOCANTES IDENTIFICADAS (> 40 palabras):")
    print("-" * 72)
    if not sofs:
        print("  ✓ Ninguna oración supera las 40 palabras. Lectura ágil garantizada.")
    else:
        print(f"  ⚠️ Se identificaron {len(sofs)} oraciones de más de 40 palabras.")
        print("  Top 5 oraciones más densas para evaluar división con punto seguido:\n")
        # Ordenar por longitud descendente
        for i, s in enumerate(sorted(sofs, key=lambda x: x["num_palabras"], reverse=True)[:5], 1):
            print(f"  [{i}] ({s['num_palabras']} palabras):")
            print(f"      «{s['texto']}»\n")

    # 8. Ruido Técnico, RUTs y Códigos Alfanuméricos
    rt = aud.get("ruido_tecnico", {})
    print("\n8. RUIDO TÉCNICO, RUTS Y CÓDIGOS ALFANUMÉRICOS:")
    print("-" * 72)
    if rt.get("es_limpio"):
        print("  ✓ Prosa narrativa 100 % limpia: Cero RUTs, códigos CVE, hashes o nombres cuádruples en el cuerpo.")
    else:
        if rt.get("total_ruts", 0) > 0:
            print(f"  ⚠️ ALERTA RUTs: Se detectaron {rt['total_ruts']} menciones de RUT en la prosa narrativa:")
            print(f"     Casos: {', '.join(set(rt['ruts_detectados']))}")
        if rt.get("total_cves", 0) > 0:
            print(f"  ⚠️ ALERTA CVEs: Se detectaron {rt['total_cves']} códigos CVE/registro en la prosa narrativa:")
            print(f"     Casos: {', '.join(set(rt['cves_detectados']))}")
        if rt.get("total_backticks_tecnicos", 0) > 0:
            print(f"  ⚠️ ALERTA CÓDIGOS BACKTICK: Se detectaron {rt['total_backticks_tecnicos']} códigos técnicos:")
            print(f"     Casos: {', '.join(set(rt['backticks_detectados']))}")
        if rt.get("total_nombres_cuadruples", 0) > 0:
            print(f"  ⚠️ ALERTA NOMBRES CUÁDRUPLES: Se detectaron {rt['total_nombres_cuadruples']} nombres legales completos:")
            print(f"     Casos: {', '.join(rt['nombres_cuadruples'][:5])}")
        print("  Sugerencia: Trasladar códigos formales a 'Fuentes documentales' y usar 'Nombre + Apellido'.")

    print("=" * 72)


if __name__ == "__main__":
    main()

