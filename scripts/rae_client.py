#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente oficial de la API de la Real Academia Española (RAE) para Última Prensa y Antigravity.
Servicio: https://rae-api.com (Organización: https://github.com/rae-api-com)
Permite consultar definiciones, etimologías, sinónimos, palabra del día y validar
el cumplimiento estricto de las normas ortográficas y de puntuación de la RAE (Ortografía 2010 / DPD).
"""

import os
import sys
import re
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_API_KEY = os.environ.get("RAE_API_KEY", "")
BASE_URL = "https://rae-api.com/api"


class RaeClient:
    """Cliente HTTP para interactuar con rae-api.com."""

    def __init__(self, api_key: str = DEFAULT_API_KEY, base_url: str = BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _request(self, endpoint: str, query_params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        if query_params:
            url += "?" + urllib.parse.urlencode(query_params)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Antigravity-RAE/1.0 (+https://ultimaprensa.cl)",
            "Accept": "application/json"
        }

        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except urllib.error.HTTPError as e:
            try:
                error_body = json.loads(e.read().decode("utf-8"))
                return error_body
            except Exception:
                return {"ok": False, "error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_word(self, word: str) -> Dict[str, Any]:
        """Obtiene la definición completa, etimología, sinónimos y antónimos de una palabra."""
        clean_word = word.strip().lower()
        endpoint = f"/words/{urllib.parse.quote(clean_word)}"
        return self._request(endpoint)

    def search(self, query: str) -> Dict[str, Any]:
        """Busca términos o expresiones en el diccionario de la RAE."""
        return self._request("/search", {"q": query})

    def get_daily_word(self) -> Dict[str, Any]:
        """Obtiene la palabra del día según la RAE."""
        return self._request("/daily")

    def get_random_word(self) -> Dict[str, Any]:
        """Obtiene una palabra aleatoria del diccionario."""
        return self._request("/random")

    @staticmethod
    def validar_normas_rae(texto: str) -> List[Dict[str, Any]]:
        """
        Audita un texto en español para detectar desviaciones respecto a las normas
        de la Real Academia Española (Ortografía 2010 y Diccionario Panhispánico de Dudas),
        especialmente vicios derivados del modelo anglosajón.
        """
        errores = []

        # 1. Puntuación dentro de comillas (estilo anglosajón: ." o ,")
        # En la norma RAE, el punto, coma, punto y coma y dos puntos van SIEMPRE FUERA de las comillas.
        patron_anglo_comillas = re.findall(r'(\w+[\.,][»"”])', texto)
        if patron_anglo_comillas:
            for match in patron_anglo_comillas[:5]:
                errores.append({
                    "tipo": "puntuacion_interior_comillas",
                    "descripcion": "En español (RAE), los signos de puntuación (.,;) van SIEMPRE fuera de las comillas de cierre.",
                    "ejemplo_detectado": match,
                    "correccion_sugerida": f"{match[:-2]}»{match[-2]}"
                })

        # 2. Comillas inglesas como comillas principales
        # La RAE prescribe prioritariamente comillas angulares o latinas (« »).
        comillas_inglesas = re.findall(r'(\s"[A-ZÁÉÍÓÚa-záéíóú0-9\s,.-]{3,}"[\s\.,])', texto)
        if comillas_inglesas:
            errores.append({
                "tipo": "comillas_anglosajonas",
                "descripcion": "Uso de comillas inglesas dobles (\") como comillas principales. La RAE prescribe comillas angulares (« »).",
                "ejemplo_detectado": comillas_inglesas[0].strip(),
                "correccion_sugerida": "Usar «...»"
            })

        # 3. Signos de interrogación o exclamación sin signo de apertura
        for linea in texto.splitlines():
            if "?" in linea and "¿" not in linea:
                partes = linea.split("?")
                for parte in partes[:-1]:
                    if not any(k in parte for k in ["http", "github", "id="]):
                        errores.append({
                            "tipo": "falta_signo_apertura_interrogacion",
                            "descripcion": "En español son obligatorios los signos dobles de interrogación (¿ ?).",
                            "ejemplo_detectado": (parte.strip()[-50:] if len(parte.strip()) > 50 else parte.strip()) + "?",
                            "correccion_sugerida": "¿" + parte.strip() + "?"
                        })
                        break

        # 4. Punto tras signo de cierre de interrogación o exclamación (?. o !.)
        punto_tras_cierre = re.findall(r'([?!]\.)', texto)
        if punto_tras_cierre:
            errores.append({
                "tipo": "punto_tras_signo_de_cierre",
                "descripcion": "El punto después de ? o ! es redundante y constituye falta ortográfica según la RAE.",
                "ejemplo_detectado": punto_tras_cierre[0],
                "correccion_sugerida": punto_tras_cierre[0][0]
            })

        # 5. Espaciado defectuoso en la raya de incisos (—)
        # RAE: la raya de apertura se escribe pegada a la primera palabra del inciso y separada de la anterior: "palabra —inciso".
        # La de cierre pegada a la última: "inciso— palabra" o "inciso—,".
        # Error anglosajón / defecto: raya con espacio antes y después ("palabra — inciso — palabra").
        rayas_flotantes = re.findall(r'(\s+—\s+)', texto)
        if rayas_flotantes:
            errores.append({
                "tipo": "espaciado_raya_inciso",
                "descripcion": "La raya de incisos no debe llevar espacios a ambos lados simultáneamente. Va pegada al texto del inciso: «palabra —inciso— palabra».",
                "ejemplo_detectado": rayas_flotantes[0],
                "correccion_sugerida": "Unir la raya a la palabra inicial o final del inciso."
            })

        # 6. Separación de porcentaje sin espacio (ej. 50% en vez de 50 %)
        porcentajes_sin_espacio = re.findall(r'(\b\d+%)', texto)
        if porcentajes_sin_espacio:
            errores.append({
                "tipo": "porcentaje_sin_espacio",
                "descripcion": "La RAE prescribe que entre la cifra y el símbolo de porcentaje (%) debe mediar un espacio (ej. 50 %).",
                "ejemplo_detectado": porcentajes_sin_espacio[0],
                "correccion_sugerida": f"{porcentajes_sin_espacio[0][:-1]} %"
            })

        # 7. Punto final en títulos y subtítulos
        lineas = texto.splitlines()
        for idx, l in enumerate(lineas):
            if l.startswith("#") and l.strip().endswith("."):
                errores.append({
                    "tipo": "punto_en_titulo",
                    "descripcion": "Los títulos y subtítulos no llevan punto final según la Ortografía de la RAE.",
                    "ejemplo_detectado": l.strip(),
                    "linea": idx + 1
                })

        # 8. Meses del año con mayúscula indebida (calco del inglés)
        meses_mayuscula = re.findall(r'\b(de\s+(?:Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)\b)', texto)
        if meses_mayuscula:
            errores.append({
                "tipo": "mes_con_mayuscula",
                "descripcion": "En español y en Chile los nombres de los meses se escriben siempre con minúscula inicial.",
                "ejemplo_detectado": meses_mayuscula[0],
                "correccion_sugerida": meses_mayuscula[0].lower()
            })

        # 9. Dígito verificador del RUT chileno con 'k' minúscula
        rut_k_minuscula = re.findall(r'\b(\d{1,2}(?:\.\d{3}){2}-k)\b', texto)
        if rut_k_minuscula:
            errores.append({
                "tipo": "rut_k_minuscula",
                "descripcion": "En el RUT / RUN chileno, el dígito verificador cuando es letra debe escribirse con K mayúscula.",
                "ejemplo_detectado": rut_k_minuscula[0],
                "correccion_sugerida": rut_k_minuscula[0][:-1] + "K"
            })

        # 10. Punto decimal anglosajón en porcentajes
        punto_decimal_pct = re.findall(r'(\b\d+\.\d+\s*%)', texto)
        if punto_decimal_pct:
            errores.append({
                "tipo": "punto_decimal_porcentaje",
                "descripcion": "En Chile (INN NCh) y según la RAE se utiliza la coma decimal en lugar del punto decimal anglosajón.",
                "ejemplo_detectado": punto_decimal_pct[0],
                "correccion_sugerida": punto_decimal_pct[0].replace(".", ",")
            })

        return errores


def main():
    if len(sys.argv) < 2:
        print("Uso: python rae_cli.py <palabra|--validar <archivo>|--diaria|--aleatoria>")
        sys.exit(1)

    client = RaeClient()
    arg = sys.argv[1]

    if arg == "--diaria":
        res = client.get_daily_word()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif arg == "--aleatoria":
        res = client.get_random_word()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif arg == "--validar" and len(sys.argv) > 2:
        archivo = sys.argv[2]
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        errs = client.validar_normas_rae(contenido)
        print(f"Auditoría RAE para {archivo}:")
        if not errs:
            print("✓ Texto cumple con los estándares ortotipográficos de la RAE.")
        else:
            print(f"✗ Se detectaron {len(errs)} observaciones según la norma RAE:")
            for e in errs:
                print(f"  - [{e['tipo']}]: {e['descripcion']} (Detectado: {e.get('ejemplo_detectado')})")
    else:
        res = client.get_word(arg)
        if res.get("ok"):
            data = res.get("data", {})
            print(f"\nPALABRA: {data.get('word')}")
            for m in data.get("meanings", []):
                origin = m.get("origin", {}).get("raw", "")
                if origin:
                    print(f"Origen: {origin}")
                for s in m.get("senses", []):
                    desc = s.get("description", "")
                    cat = s.get("category", "")
                    fields = ", ".join(s.get("fields", []) or [])
                    f_info = f" [{fields}]" if fields else ""
                    print(f"  • {cat}{f_info}: {desc}")
        else:
            print(f"Error: {res.get('error')}")
            if res.get("suggestions"):
                print(f"Sugerencias: {', '.join(res.get('suggestions'))}")


if __name__ == "__main__":
    main()
