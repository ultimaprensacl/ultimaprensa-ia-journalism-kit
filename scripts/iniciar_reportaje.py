#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicialización y Andamiaje de Nuevos Reportajes para Última Prensa.
Genera la estructura de carpetas, plantillas y archivos canónicos para iniciar
una investigación de forma inmediata conforme a los estándares de Última Prensa.
"""

import os
import sys
import argparse
import unicodedata
import re
from pathlib import Path


def normalizar_slug(texto: str) -> str:
    """Convierte un título en un slug limpio para nombres de directorio."""
    t = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    t = re.sub(r'[^\w\s-]', '', t).strip().lower()
    return re.sub(r'[-\s]+', '_', t)


def crear_estructura_reportaje(nombre: str, slug: str = None, forzar: bool = False) -> Path:
    base_dir = Path(__file__).resolve().parent.parent.parent / "reportajes"
    slug_final = slug or normalizar_slug(nombre)
    dir_reportaje = base_dir / slug_final

    if dir_reportaje.exists() and not forzar:
        print(f"⚠️ El directorio de investigación ya existe: {dir_reportaje}")
        print("Usa --forzar si deseas sobrescribir o selecciona otro nombre/slug.")
        sys.exit(1)

    dir_docs = dir_reportaje / "documentos"
    dir_fuentes = dir_reportaje / "fuentes"
    dir_notas = dir_reportaje / "notas_y_datos"

    for d in (dir_docs, dir_fuentes, dir_notas):
        d.mkdir(parents=True, exist_ok=True)

    # 1. documentos/.gitkeep
    (dir_docs / ".gitkeep").touch()

    # 2. fuentes/enlaces_fuentes.txt
    enlaces_txt = f"""# Enlaces y Fuentes Web: {nombre}

Pega aquí los enlaces (URLs) de notas de prensa, boletines oficiales o portales web relevantes para esta investigación.

Ejemplos:
- https://www.mercadopublico.cl/licitacion/...
- https://www.pjud.cl/...
- https://www.contraloria.cl/...
"""
    (dir_fuentes / "enlaces_fuentes.txt").write_text(enlaces_txt, encoding="utf-8")

    # 3. notas_y_datos/cronologia_y_datos.md
    cronologia_md = f"""# Ficha de Datos y Cronología: {nombre}

## 1. Datos Clave Extraídos de Documentos Oficiales
- **Organismos Involucrados:** 
- **Número de Contrato / Oficio / Causa Judicial:** 
- **Monto Total / Alcance Económico:** 
- **Fechas Relevantes:** 

## 2. Declaraciones Públicas Oficiales Registradas en Prensa
- **Fuente de Prensa / Fecha:** 
  - *Declaración:* 

## 3. Cronología de Hechos Probados
1. `[Fecha]`: Hito 1 (Documentado en Oficio N°...)
2. `[Fecha]`: Hito 2 (Publicado en Diario X...)
3. `[Fecha]`: Hito 3 (Auditoría o Resolución N°...)
"""
    (dir_notas / "cronologia_y_datos.md").write_text(cronologia_md, encoding="utf-8")

    # 4. reportaje_final.md
    reportaje_md = f"""[INVESTIGACIÓN ESPECIAL / FISCALIZACIÓN]
# {nombre}: [Verbo activo + Revelación central basada en documentos]

> *[Bajada del reportaje: Síntesis en cursiva de los documentos oficiales revisados, cifra o alcance del perjuicio fiscal y organismos involucrados. Estrictamente sin negrita].*

**Por la Unidad de Investigación de Última Prensa**

[Párrafos 1 y 2: Entrada directa / Lead con el hallazgo documental o dato contundente más revelador. Sin subtítulo ni encabezado de introducción].

[Párrafo 3: Nut Graf / Tuerca de la historia: Por qué este caso importa, a quiénes afecta directamente y qué demuestra la evidencia oficial contrastada].

> **Radiografía del caso en cifras y documentos:**
> - **Documentos clave revisados:** [Causas PJUD, dictámenes CGR, órdenes de compra de Mercado Público o resoluciones].
> - **Monto / Perjuicio / Inversión fiscal:** [Cifra exacta en pesos y unidades de fomento, con traducción per cápita o equivalencias comunitarias].
> - **Organismos y autoridades involucradas:** [Servicios públicos, ministerios, municipios o empresas contratistas].

---

### 1. [Ladillo 1: El origen en los registros y contratos oficiales]

[Desarrollo del primer hito con números de licitación, fechas exactas, actas y resoluciones. Párrafos estructurados como mini-historias bajo doctrina KAS].

---

### 2. [Ladillo 2: La reconstrucción según los antecedentes y declaraciones públicas]

[Declaraciones públicas previas emitidas en medios o vocerías institucionales por las personas y entidades involucradas, contrastadas con los hechos documentados].

---

### 3. [Ladillo 3: Las inconsistencias detectadas en el cruce de información]

[Comparación fáctica y cuantitativa entre lo declarado y lo que acreditan los documentos de auditoría, balances o testimonios en causas judiciales].

---

### 4. [Ladillo 4: Consecuencias jurídicas, administrativas y estado procesal]

[Dictámenes de la Contraloría General de la República, querellas criminales, sumarios en curso o procesos fiscalizadores activos].

---

### Fuentes documentales

1. Contraloría General de la República. (2026). *Informe Final de Investigación Especial N.° [X]*. División de Auditoría.
2. Poder Judicial. (2026). *Causa Rol N.° [X]-[Año]*. [Tribunal o Corte de Apelaciones respectiva].
3. Dirección de Compras y Contratación Pública. (2026). *Licitación Pública ID [X]*. Mercado Público.
4. Biblioteca del Congreso Nacional. (2026). *Ley N.° [X]*. [Materia de la ley].

---

> *Esta investigación periodística fue elaborada por la Unidad de Investigación de Última Prensa a partir del análisis forense de expedientes oficiales, registros de compras públicas y auditorías del Estado, utilizando el instrumental de [Open Legal Chile](https://github.com/elpabloultron/open-legal-chile), el [Última Prensa Journalism Kit](https://github.com/ultimaprensacl/ultimaprensa-ia-journalism-kit), [Gemini 3.8 Flash](https://deepmind.google/technologies/gemini/), [Graphify](https://github.com/Graphify-Labs/graphify) y [Google Antigravity IDE](https://antigravity.google/).*
"""
    (dir_reportaje / "reportaje_final.md").write_text(reportaje_md, encoding="utf-8")

    return dir_reportaje


def main():
    parser = argparse.ArgumentParser(
        description="Inicializa la estructura canónica para un nuevo reportaje de investigación en Última Prensa."
    )
    parser.add_argument("nombre", help="Nombre o título preliminar de la investigación.")
    parser.add_argument("--slug", help="Nombre del directorio personalizado (opcional).", default=None)
    parser.add_argument("--forzar", action="store_true", help="Sobrescribir si el directorio ya existe.")

    args = parser.parse_args()

    ruta = crear_estructura_reportaje(args.nombre, args.slug, args.forzar)

    print("=" * 65)
    print("🚀 NUEVO DOSSIER DE INVESTIGACIÓN INICIALIZADO CON ÉXITO")
    print("=" * 65)
    print(f"📁 Directorio creado: {ruta}")
    print(f"📄 Archivo principal: {ruta / 'reportaje_final.md'}")
    print(f"📂 Carpeta documentos: {ruta / 'documentos'}")
    print(f"📂 Carpeta fuentes:    {ruta / 'fuentes'}")
    print(f"📂 Carpeta notas:      {ruta / 'notas_y_datos'}")
    print("-" * 65)
    print("Próximos pasos sugeridos:")
    print(f"  1. Coloca los PDFs/documentos en: {ruta / 'documentos'}")
    print(f"  2. Procesa a Markdown con: .venv/bin/python kit-journalism/scripts/ingestar_documentos_md.py --dir \"{ruta / 'documentos'}\" --out \"{ruta / 'notas_y_datos'}\"")
    print(f"  3. Audita con: .venv/bin/python kit-journalism/scripts/verificar_reportaje.py \"{ruta / 'reportaje_final.md'}\"")
    print(f"  4. Exporta a Substack: .venv/bin/python kit-journalism/scripts/exportar_substack.py \"{ruta / 'reportaje_final.md'}\"")
    print("=" * 65)


if __name__ == "__main__":
    main()
