#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditor Pre-Publicación y Verificador de Calidad Editorial para Última Prensa.
Valida el cumplimiento estricto de las normas editoriales, ortotipográficas RAE
y de la doctrina del Manual del Editor de Investigación (KAS) antes de publicar.
"""

import os
import sys
import re
import argparse
from pathlib import Path


class AuditorReportaje:
    def __init__(self, ruta_archivo: str):
        self.ruta = Path(ruta_archivo)
        if not self.ruta.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
        self.contenido = self.ruta.read_text(encoding="utf-8")
        self.lineas = self.contenido.splitlines()
        self.errores = []
        self.advertencias = []
        self.aprobados = []

    def auditar_todo(self) -> bool:
        self.verificar_titular_y_bajada()
        self.verificar_lead_sin_subtitulo()
        self.verificar_nota_metodologica()
        self.verificar_fuentes_documentales()
        self.verificar_redundancia_territorial()
        self.verificar_cargos_en_minuscula()
        self.verificar_normas_rae_puntuacion()
        self.verificar_ruido_tecnico_y_nombres()
        self.verificar_ritmo_y_legibilidad()

        return len(self.errores) == 0

    def verificar_titular_y_bajada(self):
        # 1. Bajada en cursiva en bloque de cita y sin negrita
        encontro_bajada = False
        tiene_h2 = False
        h2_linea = 0
        for num, linea in enumerate(self.lineas[:15], 1):
            linea_s = linea.strip()
            if linea_s.startswith("> *") or linea_s.startswith(">*"):
                encontro_bajada = True
                if "**" in linea_s:
                    self.errores.append(
                        f"Línea {num}: La bajada contiene negrita (**). Regla estricta: La bajada debe ir en cursiva y estrictamente sin negrita."
                    )
                else:
                    self.aprobados.append("Bajada canónica en cursiva, en bloque de cita (> *...*) y sin negrita.")
                break
            elif linea_s.startswith("## "):
                tiene_h2 = True
                h2_linea = num

        if not encontro_bajada:
            if tiene_h2:
                self.errores.append(
                    f"Línea {h2_linea}: La bajada está formateada con encabezado H2 ('##'). Regla estricta: La bajada debe ir en bloque de cita (> *...*)."
                )
            else:
                self.advertencias.append("No se detectó un bloque de bajada (> *...*) en las primeras 15 líneas.")
        elif tiene_h2:
            self.aprobados.append("Subtítulo formal complementario H2 presente junto a la bajada canónica.")

        # 2. Sin punto final en titular (# ...)
        for num, linea in enumerate(self.lineas[:10], 1):
            linea_s = linea.strip()
            if linea_s.startswith("# "):
                if linea_s.endswith("."):
                    self.errores.append(f"Línea {num}: El titular principal termina con punto final (prohibido según normas RAE/manual de estilo).")
                else:
                    self.aprobados.append("Titular principal sin punto final de cierre.")
                break

    def verificar_lead_sin_subtitulo(self):
        # Verificar que no exista encabezado de introducción
        for num, linea in enumerate(self.lineas[:30], 1):
            linea_s = linea.strip()
            if re.match(r'^#{2,3}\s+(?:Introducción|Lead|Entrada)\b', linea_s, re.IGNORECASE):
                self.errores.append(
                    f"Línea {num}: Se detectó el encabezado '{linea_s}'. Regla estricta: El lead arranca directamente tras la firma, sin subtítulo de introducción."
                )
                return
        self.aprobados.append("El lead arranca limpiamente sin subtítulo de introducción.")

    def verificar_nota_metodologica(self):
        # 1. No debe existir encabezado '### Nota metodológica'
        for num, linea in enumerate(self.lineas, 1):
            linea_s = linea.strip()
            if re.match(r'^#{2,4}\s+Nota\s+metodol[oó]gica\b', linea_s, re.IGNORECASE):
                self.errores.append(
                    f"Línea {num}: Se detectó el encabezado '{linea_s}'. Regla estricta: La nota metodológica se dispone en bloque de cita (> *...*) y sin subtítulo."
                )

        # 2. Debe existir bloque de cierre con herramientas enlazadas
        texto_final = "\n".join(self.lineas[-120:])
        bloque_met = re.search(r'>\s*\*(?:Esta investigación periodística fue elaborada|Investigación elaborada).*?\*', texto_final, re.DOTALL | re.IGNORECASE)

        if not bloque_met:
            # Buscar cualquier bloque de cita al cierre
            bloque_met = re.search(r'>\s*\*.*?(?:Open Legal Chile|Última Prensa|Gemini).*?\*', texto_final, re.DOTALL | re.IGNORECASE)

        if bloque_met:
            contenido_bloque = bloque_met.group(0)
            herramientas_requeridas = [
                ("Open Legal Chile", "https://github.com/elpabloultron/open-legal-chile"),
                ("Última Prensa", "ultimaprensa-ia-journalism-kit"),
                ("Gemini", "gemini"),
                ("Graphify", "graphify"),
                ("Antigravity", "antigravity")
            ]
            faltantes = [h[0] for h in herramientas_requeridas if h[0].lower() not in contenido_bloque.lower()]
            if faltantes:
                self.advertencias.append(
                    f"La nota metodológica no menciona o enlaza las herramientas oficiales: {', '.join(faltantes)}."
                )
            else:
                self.aprobados.append("Nota metodológica canónica obligatoria presente, sin subtítulo y con enlaces institucionales completos.")
        else:
            self.errores.append("No se encontró el bloque canónico de Nota Metodológica en cita cursiva (> *...*) al cierre del reportaje.")

    def verificar_fuentes_documentales(self):
        encabezado_fuentes = re.search(r'^#{2,3}\s+(?:\d+\.\s*)?(?:Fuentes documentales|Base de referencias|Referencias)', self.contenido, re.MULTILINE | re.IGNORECASE)
        if encabezado_fuentes:
            self.aprobados.append("Sección obligatoria de Fuentes Documentales presente.")
        else:
            self.errores.append("Falta la sección obligatoria de 'Fuentes documentales' al cierre del reportaje (conforme a APA 7ma Edición).")

    def verificar_redundancia_territorial(self):
        # Excepciones válidas de nombres propios institucionales
        excepciones = [
            r"open legal chile",
            r"banco de chile", r"universidad de chile", r"televisión nacional de chile",
            r"policía de investigaciones de chile", r"ejército de chile", r"armada de chile",
            r"fuerza aérea de chile", r"carabineros de chile", r"cámara chilena de la construcción",
            r"asociación chilena de", r"instituto de chile", r"academia chilena de la lengua"
        ]
        texto_filtrado = self.contenido
        for exc in excepciones:
            texto_filtrado = re.sub(exc, " ", texto_filtrado, flags=re.IGNORECASE)

        # Excluir la nota metodológica y fuentes
        partes = re.split(r'^#{2,3}\s+(?:\d+\.\s*)?(?:Fuentes documentales|Base de referencias)', texto_filtrado, flags=re.MULTILINE | re.IGNORECASE)
        prosa_analizar = partes[0]

        # Limpiar enlaces markdown y URLs para evitar falsos positivos en slugs
        prosa_analizar = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', prosa_analizar)
        prosa_analizar = re.sub(r'https?://\S+', ' ', prosa_analizar)

        patron = r'\b(chile|chileno|chilena|chilenos|chilenas)\b'
        hallazgos = list(re.finditer(patron, prosa_analizar, flags=re.IGNORECASE))
        if hallazgos:
            ejemplos = [h.group(0) for h in hallazgos[:4]]
            self.advertencias.append(
                f"Regla de economía territorial: Se detectaron {len(hallazgos)} menciones de '{', '.join(set(ejemplos))}'. Omitir o sustituir por 'el Estado', 'el Fisco', 'la administración pública' cuando el contexto sea evidente."
            )
        else:
            self.aprobados.append("Cumplimiento estricto de cero redundancia territorial («Chile / chileno/a»).")

    def verificar_cargos_en_minuscula(self):
        cargos = [
            "Presidente", "Presidenta", "Ministro", "Ministra", "Biministro", "Biministra",
            "Subsecretario", "Subsecretaria", "Contralor", "Contralora", "Fiscal",
            "Alcalde", "Alcaldesa", "Gobernador", "Gobernadora", "Delegado", "Delegada",
            "Diputado", "Diputada", "Senador", "Senadora"
        ]
        texto_filtrado = re.sub(r'\b(?:Contraloría|Dirección|Secretaría|Comandancia)\s+General\b', ' ', self.contenido, flags=re.IGNORECASE)
        # Excepción para el título propio de programa radial «Aló Senador»
        texto_filtrado = re.sub(r'«Aló\s+Senador»', ' ', texto_filtrado, flags=re.IGNORECASE)
        texto_filtrado = re.sub(r'Aló\s+Senador', ' ', texto_filtrado, flags=re.IGNORECASE)
        hallazgos = []
        for cargo in cargos:
            patron = rf'(?<![\.\?\!\n]\s)\b({cargo})\b'
            for m in re.finditer(patron, texto_filtrado):
                hallazgos.append(m.group(1))

        if hallazgos:
            conteo = set(hallazgos)
            self.advertencias.append(
                f"Cargos con mayúscula inicial indebida: {', '.join(conteo)}. La norma RAE y Última Prensa exigen minúscula ('presidente', 'ministro', 'fiscal', etc.)."
            )
        else:
            self.aprobados.append("Cargos públicos e institucionales correctamente redactados en minúscula.")

    def verificar_ruido_tecnico_y_nombres(self):
        # Aislar el cuerpo narrativo (antes de Fuentes documentales)
        partes = re.split(r'^#{2,3}\s+(?:\d+\.\s*)?(?:Fuentes documentales|Base de referencias)', self.contenido, flags=re.MULTILINE | re.IGNORECASE)
        prosa_cuerpo = partes[0]
        # Remover bloques de código
        prosa_cuerpo = re.sub(r"```.*?```", " ", prosa_cuerpo, flags=re.DOTALL)

        # 1. RUTs en prosa
        ruts = re.findall(r"\b\d{1,2}\.\d{3}\.\d{3}-[\dkK]\b|\b\d{7,8}-[\dkK]\b", prosa_cuerpo)
        # 2. CVEs en prosa
        cves = re.findall(r"\bCVE\s+[`\"']?[A-Za-z0-9_-]+[`\"']?|\bCR[a-zA-Z0-9]{8,12}\b", prosa_cuerpo)
        # 3. Backticks técnicos (FA-XXXX, etc.)
        b_tecnicos = re.findall(r"`(?:FA-\d+|AC[a-zA-Z0-9]+|\d{7,8})`", prosa_cuerpo)

        errores_ruido = []
        if ruts:
            errores_ruido.append(f"Se detectaron {len(ruts)} números de RUT en la prosa narrativa ({', '.join(set(ruts[:3]))}). Deben eliminarse y reservarse a 'Fuentes documentales'.")
        if cves:
            errores_ruido.append(f"Se detectaron {len(cves)} menciones de código CVE en la prosa narrativa ({', '.join(set(cves[:3]))}). Deben reservarse a 'Fuentes documentales'.")
        if b_tecnicos:
            errores_ruido.append(f"Se detectaron {len(b_tecnicos)} códigos técnicos con backticks ({', '.join(set(b_tecnicos[:3]))}).")

        if errores_ruido:
            for er in errores_ruido:
                self.advertencias.append(f"Ruido técnico en prosa: {er}")
        else:
            self.aprobados.append("Prosa narrativa 100 % limpia de RUTs, códigos CVE y backticks técnicos.")

    def verificar_normas_rae_puntuacion(self):
        # 1. Espacio en porcentajes: '100 %' vs '100%'
        sin_espacio_pct = re.findall(r'\b\d+(?:,\d+)?%', self.contenido)
        if sin_espacio_pct:
            self.advertencias.append(
                f"Porcentajes sin espacio obligatorio según norma RAE: detectados {len(sin_espacio_pct)} casos (ej. '{sin_espacio_pct[0]}'). Debe ser '100 %'."
            )
        else:
            self.aprobados.append("Espacio normativo correcto entre cifra y porcentaje (ej. '100 %').")

        # 2. Coma decimal chilena: detectar puntos decimales en números (ej. '12.5 %')
        punto_decimal = re.findall(r'\b\d+\.\d+\s*%', self.contenido)
        if punto_decimal:
            self.advertencias.append(
                f"Punto decimal anglosajón detectado en porcentaje: {punto_decimal[:3]}. Norma técnica chilena exige coma decimal (ej. '12,5 %')."
            )
        else:
            self.aprobados.append("Notación decimal conforme a norma técnica chilena (coma decimal).")

        # 3. Puntuación fuera de comillas: detectar '.",' o '.,' o '?"'
        puntuacion_dentro = re.findall(r'[«"][^»"]+[\.,;][»"]', self.contenido)
        if puntuacion_dentro:
            self.advertencias.append(
                f"Signo de puntuación dentro de comillas detectado en {len(puntuacion_dentro)} casos (ej. {puntuacion_dentro[0]}). Regla RAE: La puntuación siempre va fuera de las comillas."
            )
        else:
            self.aprobados.append("Signos de puntuación correctamente situados fuera de comillas.")

    def verificar_ritmo_y_legibilidad(self):
        try:
            from auditor_estilo_y_redaccion import AuditorEstiloRedaccion
            aud = AuditorEstiloRedaccion()
            res = aud.generar_auditoria_completa(self.contenido)
            leg = res.get("legibilidad", {})
            ritmo = res.get("ritmo", {})
            sz = leg.get("szigriszt_pazos")
            if sz is not None:
                self.aprobados.append(f"Legibilidad Flesch-Szigriszt: {sz} puntos ({leg.get('nivel_inflesz')}).")
            if ritmo:
                prom = ritmo.get("longitud_promedio_palabras")
                sof = ritmo.get("porcentaje_sofocantes", 0)
                if sof > 40:
                    self.advertencias.append(
                        f"Densidad sintáctica: {sof} % de oraciones superan 40 palabras (promedio: {prom} pal/oración). Se aconseja intercalar oraciones breves de impacto (KAS Cap. 8)."
                    )
                else:
                    self.aprobados.append(f"Ritmo narrativo equilibrado: promedio de {prom} palabras por oración.")
        except Exception:
            pass

    def imprimir_reporte(self):
        print("\n" + "=" * 70)
        print(f"📋 INFORME DE VERIFICACIÓN EDITORIAL PRE-PUBLICACIÓN: {self.ruta.name}")
        print("=" * 70)

        print("\n[✓] VERIFICACIONES SUPERADAS CON ÉXITO:")
        for ap in self.aprobados:
            print(f"  • {ap}")

        if self.advertencias:
            print("\n[⚠️] ADVERTENCIAS EDITORIALES (REVISIÓN RECOMENDADA):")
            for adv in self.advertencias:
                print(f"  • {adv}")

        if self.errores:
            print("\n[❌] ERRORES BLOQUEANTES QUE DEBEN CORREGIRSE:")
            for err in self.errores:
                print(f"  • {err}")
            print("\n" + "=" * 70)
            print("ESTADO: ❌ NO APTO PARA PUBLICACIÓN HASTA RESOLVER LOS ERRORES BLOQUEANTES")
            print("=" * 70 + "\n")
        else:
            print("\n" + "=" * 70)
            print("ESTADO: 🚀 APTO PARA EXPORTACIÓN Y PUBLICACIÓN EN SUBSTACK")
            print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Audita un reportaje Markdown contra los estándares editoriales y de rigor de Última Prensa."
    )
    parser.add_argument("archivo", help="Ruta al archivo Markdown del reportaje.")
    args = parser.parse_args()

    auditor = AuditorReportaje(args.archivo)
    ok = auditor.auditar_todo()
    auditor.imprimir_reporte()

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
