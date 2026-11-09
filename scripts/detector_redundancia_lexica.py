#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detector_redundancia_lexica.py — Auditor Avanzado de Redundancia Léxica, Cohesión Referencial
y Diversidad Estilística para Última Prensa.

Herramienta de control de calidad editorial basada en NLP (NLTK Snowball Stemmer,
Open Multilingual WordNet para español, métricas MATTR/TTR y patrones estilísticos).

Capacidades de auditoría:
1. Control de redundancia territorial obligatoria («Chile / chileno/a»).
2. Control de cargos públicos en minúscula (normas RAE / ASALE).
3. Detección de proximidad crítica (martilleo léxico) por raíz/lema en ventanas cortas (< 25-30 palabras).
4. Detección de saturación intra-párrafo (palabras o raíces repetidas >= 3 veces en un párrafo).
5. Análisis de palabras hiperfrecuentes en el artículo con sugerencias dinámicas de sinónimos (WordNet OMW spa).
6. Detección de muletillas, frases de relleno y clichés periodísticos.
7. Detección de fatiga adverbial (exceso de adverbios en «-mente»).
8. Detección de repetición de inicios de oración (anáfora involuntaria).
9. Métricas de riqueza léxica: Type-Token Ratio (TTR) y Moving-Average TTR (MATTR-50).
"""

import os
import re
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List, Set, Tuple

# Carga de NLTK (Stemmer y WordNet español) con fallback defensivo
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem.snowball import SnowballStemmer

    try:
        STOPWORDS_ES = set(stopwords.words("spanish"))
    except Exception:
        nltk.download("stopwords", quiet=True)
        STOPWORDS_ES = set(stopwords.words("spanish"))

    STEMMER_ES = SnowballStemmer("spanish")

    # WordNet OMW spa
    try:
        from nltk.corpus import wordnet as wn
        # Prueba de acceso
        _ = wn.synsets("prueba", lang="spa")
        WORDNET_DISPONIBLE = True
    except Exception:
        try:
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-2.0", quiet=True)
            from nltk.corpus import wordnet as wn
            WORDNET_DISPONIBLE = True
        except Exception:
            WORDNET_DISPONIBLE = False
except Exception:
    STEMMER_ES = None
    WORDNET_DISPONIBLE = False
    STOPWORDS_ES = set()

# Stopwords ampliadas en español para análisis estilístico periodístico
PALABRAS_VACIAS_BASE = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "al",
    "en", "por", "para", "con", "sin", "sobre", "tras", "durante", "mediante",
    "y", "e", "o", "u", "ni", "que", "se", "su", "sus", "como", "mas", "pero",
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquel", "aquella",
    "es", "son", "fue", "fueron", "era", "eran", "ser", "ha", "han", "había", "habían",
    "no", "si", "ya", "le", "les", "lo", "me", "nos", "te", "muy", "más", "menos",
    "todo", "toda", "todos", "todas", "otro", "otra", "otros", "otras", "mismo", "misma",
    "entre", "hasta", "hacia", "desde", "según", "donde", "cuando", "quien", "quienes",
    "cual", "cuales", "cada", "tanto", "tanta", "tuntos", "tantas", "algo", "nada",
    "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
    "primer", "primera", "segundo", "segunda", "tercero", "tercera"
}
STOPWORDS_COMPLETAS: Set[str] = PALABRAS_VACIAS_BASE.union(STOPWORDS_ES)

# Diccionario especializado de correferentes y variación institucional para investigación
CORREFERENTES_ESPECIALIZADOS = {
    "senador": ["el parlamentario", "el legislador", "el miembro de la Cámara Alta", "el representante"],
    "senadores": ["los parlamentarios", "los legisladores", "los miembros de la Cámara Alta", "los representantes"],
    "diputado": ["el parlamentario", "el legislador", "el representante de la Cámara Baja"],
    "diputados": ["los parlamentarios", "los legisladores", "los miembros de la Cámara de Diputadas y Diputados"],
    "alcalde": ["el jefe comunal", "la autoridad edilicia", "el titular del municipio", "el edil"],
    "alcaldesa": ["la jefa comunal", "la autoridad edilicia", "la titular del municipio", "la edil"],
    "concejal": ["el representante comunal", "el miembro del concejo municipal", "el edil"],
    "factura": ["el documento tributario", "el comprobante mercantil", "el cobro", "la emisión tributaria"],
    "facturas": ["los documentos tributarios", "los comprobantes mercantiles", "las emisiones", "los cobros"],
    "dinero": ["los recursos fiscales", "el erario", "los fondos públicos", "el capital", "los caudales"],
    "recursos": ["los fondos", "el erario", "las asignaciones", "el patrimonio fiscal", "los caudales"],
    "pago": ["el desembolso", "la transferencia", "la liquidación", "el giro contable"],
    "pagos": ["los desembolsos", "las transferencias", "las liquidaciones", "los giros contables"],
    "empresa": ["la sociedad comercial", "la proveedora", "la firma", "la entidad mercantil"],
    "empresas": ["las sociedades comerciales", "las firmas proveedoras", "las compañías", "las mercantiles"],
    "radio": ["la emisora", "la estación radial", "la frecuencia", "la señal comunal"],
    "radios": ["las emisoras", "las estaciones", "las frecuencias", "las señales locales"],
    "documento": ["el expediente", "el escrito", "el instrumento público", "la resolución"],
    "documentos": ["los expedientes", "los legajos", "los antecedentes", "los instrumentos públicos"],
    "contrato": ["el convenio", "el vínculo jurídico", "el acuerdo de prestación", "el instrumento contractual"],
    "auditoría": ["el informe de control", "la indagatoria contable", "el peritaje fiscalizador", "la inspección técnica"],
    "municipio": ["la casa consistorial", "la corporación edilicia", "la administración local", "el gobierno comunal"],
    "fondos": ["los recursos", "el erario", "los caudales públicos", "el capital fiscal"]
}

# Muletillas y clichés periodísticos que desgastan la prosa
MULETILLAS_PERIODISTICAS = [
    (r"\ben el marco de\b", "en el marco de", "Reemplazar por 'durante', 'en', 'bajo' o 'con motivo de'."),
    (r"\bcabe señalar que\b", "cabe señalar que", "Fórmula de relleno. Omitir e iniciar directamente con el dato fáctico."),
    (r"\bcabe destacar que\b", "cabe destacar que", "Fórmula de relleno. Omitir y presentar el dato directamente."),
    (r"\bes importante consignar que\b", "es importante consignar que", "Fórmula de relleno. Omitir."),
    (r"\bpor su parte\b", "por su parte", "Muletilla de enlace repetitiva. Usar punto seguido o conectar con el sujeto directo."),
    (r"\ba raíz de\b", "a raíz de", "Variar con 'tras', 'a causa de', 'debido a' o 'producto de'."),
    (r"\ben ese sentido\b", "en ese sentido", "Transición trillada. Redactar el vínculo causal de forma directa."),
    (r"\ben este contexto\b", "en este contexto", "Muletilla situacional. Conectar con el hecho precedente sin fórmula."),
    (r"\bdar cuenta de\b", "dar cuenta de", "Variar con 'revelar', 'acreditar', 'consignar', 'demostrar' o 'exponer'."),
    (r"\bllevar a cabo\b", "llevar a cabo", "Verbo comodín. Usar verbos precisos: 'ejecutar', 'realizar', 'tramitar', 'efectuar'."),
    (r"\bun sinnúmero de\b", "un sinnúmero de", "Imprecisión retórica. Usar la cifra exacta o 'decenas', 'múltiples', 'diversos'."),
    (r"\bde cara a\b", "de cara a", "Anglicismo estilístico. Usar 'ante', 'frente a', 'con miras a' o 'para'."),
    (r"\bponer de relieve\b", "poner de relieve", "Cliché ensayístico. Usar 'evidenciar', 'subrayar', 'relevar' o 'constatar'."),
    (r"\ben tanto que\b", "en tanto que", "Conector pesado. Usar 'mientras' o reestructurar con punto y coma.")
]


def stem_palabra(palabra: str) -> str:
    """Retorna la raíz de la palabra usando el stemmer de Snowball en español."""
    w = palabra.lower()
    if STEMMER_ES:
        return STEMMER_ES.stem(w)
    # Fallback básico si no hay NLTK
    return re.sub(r"(es|as|os|ar|er|ir|ado|ido|ando|iendo|ción|ciones)$", "", w)


def buscar_sinonimos_wordnet(palabra: str) -> List[str]:
    """Obtiene sinónimos en español desde WordNet OMW."""
    if not WORDNET_DISPONIBLE:
        return []
    palabra_norm = palabra.lower().strip()
    sinonimos = set()
    try:
        from nltk.corpus import wordnet as wn
        for syn in wn.synsets(palabra_norm, lang="spa"):
            for lemma in syn.lemma_names("spa"):
                l_clean = lemma.replace("_", " ").lower()
                if l_clean != palabra_norm and len(l_clean) > 2:
                    sinonimos.add(l_clean)
    except Exception:
        pass
    return sorted(list(sinonimos))[:5]


class DetectorRedundanciaAvanzado:
    """Motor de análisis de redundancia léxica, morfología y diversidad de prosa."""

    def __init__(self, ventana_proximidad: int = 30, umbral_saturacion: int = 3):
        self.ventana = ventana_proximidad
        self.umbral_saturacion = umbral_saturacion

    def extraer_prosa_periodistica(self, markdown_text: str) -> str:
        """Excluye la sección final de fuentes y referencias para auditar la prosa pura."""
        partes = re.split(
            r"^#{2,3}\s+(?:\d+\.\s*)?(?:Fuentes documentales|Base de referencias|Obras citadas|Referencias)",
            markdown_text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        return partes[0]

    def limpiar_texto(self, markdown_text: str) -> str:
        """Remueve tablas, bloques de código y enlaces para analizar la prosa editorial."""
        t = self.extraer_prosa_periodistica(markdown_text)
        t = re.sub(r"```.*?```", "", t, flags=re.DOTALL)
        t = re.sub(r"^\s*\|.*\|\s*$", " ", t, flags=re.MULTILINE)
        t = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", t)
        t = re.sub(r"https?://\S+", " ", t)
        t = re.sub(r"[#>*_`]", " ", t)
        return t

    def extraer_palabras_prosa(self, texto: str) -> List[Tuple[str, str, int]]:
        """Extrae tuplas de (palabra_original, stem, posicion_indice)."""
        tokens = re.finditer(r"\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{3,}\b", texto)
        lista = []
        for idx, m in enumerate(tokens):
            w = m.group(0)
            st = stem_palabra(w)
            lista.append((w, st, idx))
        return lista

    def calcular_diversidad_lexica(self, texto_limpio: str) -> Dict[str, Any]:
        """Calcula métricas estándar de riqueza de vocabulario (TTR, MATTR-50, Hapax)."""
        palabras = re.findall(r"\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{3,}\b", texto_limpio.lower())
        tokens_contenido = [w for w in palabras if w not in STOPWORDS_COMPLETAS]
        total_tokens = len(tokens_contenido)
        if total_tokens == 0:
            return {"ttr": 0.0, "mattr_50": 0.0, "hapax_pct": 0.0, "total_palabras_contenido": 0}

        tipos_unicos = len(set(tokens_contenido))
        ttr = tipos_unicos / total_tokens

        # Conteo de palabras que aparecen exactamente una vez (Hapax Legomena)
        conteos = Counter(tokens_contenido)
        hapax = sum(1 for _, c in conteos.items() if c == 1)
        hapax_pct = (hapax / total_tokens) * 100.0

        # Moving-Average TTR con ventana de 50 tokens
        window_size = 50
        if total_tokens <= window_size:
            mattr = ttr
        else:
            ttrs_ventanas = []
            for i in range(total_tokens - window_size + 1):
                chunk = tokens_contenido[i : i + window_size]
                ttrs_ventanas.append(len(set(chunk)) / window_size)
            mattr = sum(ttrs_ventanas) / len(ttrs_ventanas)

        return {
            "total_palabras_contenido": total_tokens,
            "vocabulario_unico": tipos_unicos,
            "ttr": round(ttr, 4),
            "mattr_50": round(mattr, 4),
            "hapax_pct": round(hapax_pct, 2),
        }

    def analizar_proximidad_lemas(self, texto_limpio: str) -> List[Dict[str, Any]]:
        """Detecta repeticiones a corta distancia (< ventana) por raíz léxica (stem/lema)."""
        palabras_con_info = self.extraer_palabras_prosa(texto_limpio)
        alertas = []
        historial_stem = defaultdict(list)

        for w_orig, st, idx in palabras_con_info:
            w_norm = w_orig.lower()
            if w_norm in STOPWORDS_COMPLETAS or len(w_norm) < 4:
                continue

            if st in historial_stem:
                ultimas_pos = historial_stem[st]
                if ultimas_pos:
                    w_prev, prev_idx = ultimas_pos[-1]
                    dist = idx - prev_idx
                    if dist <= self.ventana:
                        # Obtener sugerencias correferenciales
                        sugs = CORREFERENTES_ESPECIALIZADOS.get(w_norm) or CORREFERENTES_ESPECIALIZADOS.get(w_prev) or buscar_sinonimos_wordnet(w_norm)
                        alertas.append({
                            "palabra_1": w_prev,
                            "palabra_2": w_orig,
                            "raiz_comun": st,
                            "distancia": dist,
                            "indice": idx,
                            "sugerencias": sugs[:4]
                        })
            historial_stem[st].append((w_orig, idx))

        return alertas

    def analizar_parrafos_saturados(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Identifica párrafos donde una misma raíz o concepto se reitera 3+ veces."""
        texto_prosa = self.extraer_prosa_periodistica(markdown_text)
        bloques = [
            p.strip()
            for p in re.split(r"\n\s*\n|\n(?=\s*(?:\d+\.|[-*])\s+)", texto_prosa)
            if p.strip()
        ]
        reporte = []

        for num_p, p in enumerate(bloques, 1):
            if p.startswith("#") or p.startswith("|") or len(p) < 40:
                continue
            p_limpio = re.sub(r"https?://\S+|[#>*_`]", " ", p)
            palabras = re.findall(r"\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{4,}\b", p_limpio.lower())
            significativas = [w for w in palabras if w not in STOPWORDS_COMPLETAS]

            # Agrupar por stem
            stems_map = defaultdict(list)
            for w in significativas:
                stems_map[stem_palabra(w)].append(w)

            saturadas = {}
            for st, tokens in stems_map.items():
                if len(tokens) >= self.umbral_saturacion:
                    saturadas[tokens[0]] = {
                        "veces": len(tokens),
                        "variaciones": list(set(tokens)),
                        "raiz": st,
                        "sugerencias": CORREFERENTES_ESPECIALIZADOS.get(tokens[0]) or buscar_sinonimos_wordnet(tokens[0])
                    }

            if saturadas:
                reporte.append({
                    "parrafo": num_p,
                    "fragmento": p[:140].replace("\n", " ") + "...",
                    "repeticiones": saturadas
                })

        return reporte

    def analizar_palabras_hiperfrecuentes(self, texto_limpio: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """Lista las raíces y términos con mayor densidad en todo el reportaje."""
        palabras = re.findall(r"\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{4,}\b", texto_limpio.lower())
        significativas = [w for w in palabras if w not in STOPWORDS_COMPLETAS]
        if not significativas:
            return []

        stems_map = defaultdict(list)
        for w in significativas:
            stems_map[stem_palabra(w)].append(w)

        ranking = []
        for st, tokens in sorted(stems_map.items(), key=lambda x: len(x[1]), reverse=True)[:top_n]:
            term_rep = Counter(tokens).most_common(1)[0][0]
            sugs = CORREFERENTES_ESPECIALIZADOS.get(term_rep) or buscar_sinonimos_wordnet(term_rep)
            ranking.append({
                "termino_principal": term_rep,
                "raiz": st,
                "frecuencia_total": len(tokens),
                "variaciones_en_texto": list(set(tokens)),
                "sugerencias": sugs[:4]
            })
        return ranking

    def analizar_cliches_y_muletillas(self, texto: str) -> List[Dict[str, Any]]:
        """Identifica frases de relleno o clichés periodísticos en la prosa."""
        alertas = []
        for patron, nombre, sug in MULETILLAS_PERIODISTICAS:
            for match in re.finditer(patron, texto, flags=re.IGNORECASE):
                start = max(0, match.start() - 35)
                end = min(len(texto), match.end() + 35)
                ctx = texto[start:end].strip().replace("\n", " ")
                alertas.append({
                    "muletilla": nombre,
                    "contexto": f"...{ctx}...",
                    "sugerencia": sug
                })
        return alertas

    def analizar_fatiga_adverbial(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Detecta acumulación excesiva de adverbios en '-mente' en un mismo párrafo o a corta distancia."""
        texto_prosa = self.extraer_prosa_periodistica(markdown_text)
        bloques = [
            p.strip()
            for p in re.split(r"\n\s*\n|\n(?=\s*(?:\d+\.|[-*])\s+)", texto_prosa)
            if p.strip()
        ]
        alertas = []

        for num_p, p in enumerate(bloques, 1):
            if p.startswith("#") or p.startswith("|") or len(p) < 40:
                continue
            advs = re.findall(r"\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+mente\b", p.lower())
            if len(advs) >= 3:
                alertas.append({
                    "parrafo": num_p,
                    "total_adverbios": len(advs),
                    "adverbios": advs,
                    "fragmento": p[:130].replace("\n", " ") + "...",
                    "sugerencia": "Reducir adverbios en '-mente'. Sustituir por locuciones precisas o reestructurar con verbos fuertes."
                })
        return alertas

    def analizar_inicios_oracion(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Detecta repetición de inicios de oración consecutivos (anáfora involuntaria)."""
        texto_prosa = self.limpiar_texto(markdown_text)
        # Dividir por oraciones
        oraciones = re.split(r"(?<=[\.\?!])\s+", texto_prosa)
        inicios = []
        for o in oraciones:
            o_clean = o.strip()
            m = re.match(r"^([a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{3,})\b", o_clean)
            if m:
                inicios.append((m.group(1).lower(), o_clean[:70]))

        alertas = []
        for i in range(len(inicios) - 2):
            w1, ctx1 = inicios[i]
            w2, ctx2 = inicios[i + 1]
            w3, ctx3 = inicios[i + 2]
            if w1 == w2 == w3 and w1 not in {"según", "tras"}:
                alertas.append({
                    "palabra_repetida": w1,
                    "oracion_1": f"{ctx1}...",
                    "oracion_2": f"{ctx2}...",
                    "oracion_3": f"{ctx3}...",
                    "sugerencia": "Variar la apertura de las oraciones para dinamizar la lectura."
                })
        return alertas

    def analizar_redundancia_territorial(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Audita el cumplimiento de la regla: Prohibición de redundancia territorial ('Chile', 'chileno/a')."""
        texto_prosa = self.limpiar_texto(markdown_text)
        excepciones = [
            r"open legal chile",
            r"banco de chile", r"universidad de chile", r"televisión nacional de chile",
            r"policía de investigaciones de chile", r"ejército de chile", r"armada de chile",
            r"fuerza aérea de chile", r"carabineros de chile", r"cámara chilena de la construcción",
            r"asociación chilena de", r"instituto de chile", r"academia chilena de la lengua"
        ]
        texto_filtrado = texto_prosa
        for exc in excepciones:
            texto_filtrado = re.sub(exc, " ", texto_filtrado, flags=re.IGNORECASE)

        patron = r"\b(chile|chileno|chilena|chilenos|chilenas)\b"
        alertas = []
        for match in re.finditer(patron, texto_filtrado, flags=re.IGNORECASE):
            palabra = match.group(0)
            start = max(0, match.start() - 40)
            end = min(len(texto_filtrado), match.end() + 40)
            contexto = texto_filtrado[start:end].strip().replace("\n", " ")
            alertas.append({
                "palabra": palabra,
                "contexto": f"...{contexto}...",
                "sugerencia": "Sustituir por 'el Estado', 'el Fisco', 'la legislación', 'el ordenamiento jurídico', 'la administración pública' o 'el país'."
            })
        return alertas

    def analizar_cargos_mayusculas(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Audita que los cargos públicos e institucionales se escriban en minúscula conforme a normas RAE."""
        cargos = [
            "Presidente", "Presidenta", "Ministro", "Ministra", "Biministro", "Biministra",
            "Subsecretario", "Subsecretaria", "Contralor", "Contralora", "Fiscal",
            "Alcalde", "Alcaldesa", "Gobernador", "Gobernadora", "Delegado", "Delegada",
            "Diputado", "Diputada", "Senador", "Senadora", "Juez", "Jueza", "General"
        ]
        texto_prosa = self.extraer_prosa_periodistica(markdown_text)
        # Excluir nombres institucionales válidos
        texto_prosa_filtrado = re.sub(
            r"\b(?:Contraloría|Dirección|Secretaría|Comandancia)\s+General\b", " ", texto_prosa, flags=re.IGNORECASE
        )
        # Excluir programas o marcas como «Aló Senador»
        texto_prosa_filtrado = re.sub(r"«Aló\s+Senador»", " ", texto_prosa_filtrado, flags=re.IGNORECASE)

        alertas = []
        for cargo in cargos:
            patron = rf"(?<![\.\?\!\n]\s)\b({cargo})\b"
            for match in re.finditer(patron, texto_prosa_filtrado):
                start = max(0, match.start() - 30)
                end = min(len(texto_prosa_filtrado), match.end() + 30)
                contexto = texto_prosa_filtrado[start:end].strip().replace("\n", " ")
                alertas.append({
                    "cargo": match.group(1),
                    "contexto": f"...{contexto}...",
                    "sugerencia": f"Escribir '{cargo.lower()}' con minúscula inicial (norma RAE)."
                })
        return alertas

    def generar_diagnostico(self, markdown_text: str) -> Dict[str, Any]:
        """Genera un diagnóstico global consolidado de economía léxica y calidad estilística."""
        texto_limpio = self.limpiar_texto(markdown_text)

        diversidad = self.calcular_diversidad_lexica(texto_limpio)
        proximidad_critica = self.analizar_proximidad_lemas(texto_limpio)
        parrafos_saturados = self.analizar_parrafos_saturados(markdown_text)
        ranking_frecuentes = self.analizar_palabras_hiperfrecuentes(texto_limpio, top_n=15)
        cliches = self.analizar_cliches_y_muletillas(texto_limpio)
        fatiga_adv = self.analizar_fatiga_adverbial(markdown_text)
        inicios_repetidos = self.analizar_inicios_oracion(markdown_text)
        alertas_territoriales = self.analizar_redundancia_territorial(markdown_text)
        alertas_cargos = self.analizar_cargos_mayusculas(markdown_text)

        # Compatibilidad con diccionario anterior de entidades
        conteos_entidades = {}
        for ent, sugerencias in CORREFERENTES_ESPECIALIZADOS.items():
            patron = rf"\b{re.escape(ent)}\b"
            coincidencias = len(re.findall(patron, texto_limpio, re.IGNORECASE))
            if coincidencias > 0:
                conteos_entidades[ent] = {
                    "total": coincidencias,
                    "sugerencias": sugerencias
                }

        return {
            "diversidad": diversidad,
            "entidades": conteos_entidades,
            "proximidad_critica": [a for a in proximidad_critica if a["distancia"] <= 25],
            "parrafos_saturados": parrafos_saturados,
            "ranking_hiperfrecuentes": ranking_frecuentes,
            "cliches_muletillas": cliches,
            "fatiga_adverbial": fatiga_adv,
            "inicios_repetidos": inicios_repetidos,
            "redundancia_territorial": alertas_territoriales,
            "cargos_mayusculas": alertas_cargos,
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Auditor Avanzado de Redundancia Léxica, Cohesión y Estilo para Última Prensa."
    )
    parser.add_argument("archivo", help="Ruta al archivo Markdown del reportaje a auditar.")
    parser.add_argument("--ventana", type=int, default=25, help="Ventana de palabras para proximidad crítica (default: 25).")
    parser.add_argument("--umbral", type=int, default=3, help="Umbral de repeticiones en un mismo párrafo (default: 3).")

    args = parser.parse_args()

    if not os.path.exists(args.archivo):
        print(f"Error: No se encontró el archivo {args.archivo}")
        sys.exit(1)

    with open(args.archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    detector = DetectorRedundanciaAvanzado(ventana_proximidad=args.ventana, umbral_saturacion=args.umbral)
    diag = detector.generar_diagnostico(contenido)

    print("=" * 70)
    print(f"ANÁLISIS DE REDUNDANCIA Y COHESIÓN REFERENCIAL: {os.path.basename(args.archivo)}")
    print("=" * 70)

    # 1. Diversidad Léxica
    div = diag["diversidad"]
    print("\n1. ÍNDICE DE RIQUEZA Y DIVERSIDAD LÉXICA:")
    print("-" * 70)
    print(f"  • Palabras de contenido analizadas: {div['total_palabras_contenido']}")
    print(f"  • Vocabulario único (lemas/tipos):   {div['vocabulario_unico']}")
    print(f"  • Type-Token Ratio (TTR):            {div['ttr']} (Ideal > 0.40)")
    print(f"  • Moving-Average TTR (MATTR-50):     {div['mattr_50']} (Ideal > 0.65)")
    print(f"  • Vocabulario de uso único (Hapax):  {div['hapax_pct']} %")

    # 2. Control Territorial
    print("\n2. CONTROL DE REDUNDANCIA TERRITORIAL («Chile / chileno/a»):")
    print("-" * 70)
    if not diag["redundancia_territorial"]:
        print("✓ Cumplimiento estricto: Cero redundancia territorial en la prosa analizada.")
    else:
        print(f"⚠️ Se detectaron {len(diag['redundancia_territorial'])} usos de vocabulario territorial que deben evaluarse:")
        for al in diag["redundancia_territorial"][:5]:
            print(f"  • Término «{al['palabra']}» en: {al['contexto']}")
            print(f"    -> {al['sugerencia']}")

    # 3. Control de Cargos
    print("\n3. CONTROL DE CARGOS PÚBLICOS EN MINÚSCULA (Norma RAE):")
    print("-" * 70)
    if not diag["cargos_mayusculas"]:
        print("✓ Cumplimiento estricto: Todos los cargos evaluados figuran en minúscula.")
    else:
        print(f"⚠️ Se detectaron {len(diag['cargos_mayusculas'])} cargos con mayúscula indebida:")
        for al in diag["cargos_mayusculas"][:5]:
            print(f"  • Cargo «{al['cargo']}» en: {al['contexto']}")
            print(f"    -> {al['sugerencia']}")

    # 4. Palabras Hiperfrecuentes y Sugerencias de Sinónimos
    print("\n4. TÉRMINOS HIPERFRECUENTES Y SUGERENCIAS CORREFERENCIALES:")
    print("-" * 70)
    for item in diag["ranking_hiperfrecuentes"][:10]:
        alerta = "⚠️ [REPETICIÓN ALTA]" if item["frecuencia_total"] >= 15 else "ℹ️"
        variaciones = ", ".join(item["variaciones_en_texto"][:4])
        print(f"{alerta} «{item['termino_principal'].upper()}» ({item['frecuencia_total']} veces) [Formas: {variaciones}]")
        if item["sugerencias"]:
            sugs = ", ".join(item["sugerencias"])
            print(f"    Sugerencias de variación: {sugs}")

    # 5. Proximidad Crítica (Martilleo Léxico)
    print("\n5. ALERTAS DE CERCANÍA INMEDIATA (Distancia <= 25 palabras):")
    print("-" * 70)
    if not diag["proximidad_critica"]:
        print("✓ No se detectaron martilleos o repeticiones a distancia crítica.")
    else:
        # Filtrar repeticiones únicas
        vistos = set()
        filtradas = []
        for al in diag["proximidad_critica"]:
            clave = (al["raiz_comun"], al["distancia"])
            if clave not in vistos:
                vistos.add(clave)
                filtradas.append(al)

        for al in filtradas[:10]:
            sug_txt = f" -> Sugerencia: {', '.join(al['sugerencias'][:2])}" if al["sugerencias"] else ""
            if al["palabra_1"].lower() == al["palabra_2"].lower():
                print(f"  • Palabra «{al['palabra_1']}» repetida tras solo {al['distancia']} palabras{sug_txt}")
            else:
                print(f"  • Raíz común «{al['raiz_comun']}» («{al['palabra_1']}» y «{al['palabra_2']}») a solo {al['distancia']} palabras{sug_txt}")

    # 6. Saturación en un Mismo Párrafo
    print("\n6. PÁRRAFOS CON ALTA CONCENTRACIÓN DEL MISMO LEMA (>= 3 veces):")
    print("-" * 70)
    if not diag["parrafos_saturados"]:
        print("✓ Ningún párrafo supera el límite de repeticiones del mismo término.")
    else:
        for ps in diag["parrafos_saturados"][:5]:
            print(f"  • Párrafo {ps['parrafo']}:")
            for w, info in ps["repeticiones"].items():
                sugs = f" (Sugerencias: {', '.join(info['sugerencias'][:2])})" if info["sugerencias"] else ""
                print(f"    - Término «{w}» repetido {info['veces']} veces {sugs}")
            print(f"    - Fragmento: {ps['fragmento']}\n")

    # 7. Clichés y Muletillas
    print("7. DETECCIÓN DE CLICHÉS Y MULETILLAS PERIODÍSTICAS:")
    print("-" * 70)
    if not diag["cliches_muletillas"]:
        print("✓ Cero muletillas o clichés detectados en la prosa.")
    else:
        for cl in diag["cliches_muletillas"][:6]:
            print(f"  • Muletilla «{cl['muletilla']}» en: {cl['contexto']}")
            print(f"    -> {cl['sugerencia']}")

    # 8. Fatiga Adverbial (-mente)
    print("\n8. FATIGA ADVERBIAL (Adverbios en «-mente» concentrados):")
    print("-" * 70)
    if not diag["fatiga_adverbial"]:
        print("✓ Prosa limpia de acumulación de adverbios en «-mente».")
    else:
        for fa in diag["fatiga_adverbial"][:4]:
            print(f"  • Párrafo {fa['parrafo']} contiene {fa['total_adverbios']} adverbios en '-mente' ({', '.join(fa['adverbios'])}):")
            print(f"    - Fragmento: {fa['fragmento']}")
            print(f"    -> {fa['sugerencia']}\n")

    # 9. Inicios de Oración Repetidos
    print("9. REPETICIÓN DE INICIOS DE ORACIÓN (Anáfora involuntaria):")
    print("-" * 70)
    if not diag["inicios_repetidos"]:
        print("✓ Variación adecuada en la apertura de oraciones consecutivas.")
    else:
        for ir in diag["inicios_repetidos"][:3]:
            print(f"  • Tres oraciones consecutivas inician con «{ir['palabra_repetida'].capitalize()}»:")
            print(f"    1) {ir['oracion_1']}")
            print(f"    2) {ir['oracion_2']}")
            print(f"    3) {ir['oracion_3']}")
            print(f"    -> {ir['sugerencia']}\n")

    print("=" * 70)


if __name__ == "__main__":
    main()
