# Sistema de Reportajes y Columnas de Última Prensa: Guía Operativa y Metodología

Bienvenido al espacio de trabajo de **Última Prensa** (ultimaprensa.cl). Esta guía detalla la metodología y el funcionamiento del sistema para crear reportajes de fiscalización y columnas de opinión a partir de **documentos oficiales, datos públicos y fuentes primarias**.

---

## 🔍 1. Metodología: Periodismo de Investigación Documental y Columnas Fundadas

Este enfoque de investigación (*Document-based Investigative Journalism* o *Desk Research*) es una de las ramas más rigurosas del periodismo de datos y fiscalización pública.

### Principios Centrales
1. **Evidencia Documental Primaria (*Paper Trail*):** La base de cada investigación son los documentos oficiales vinculantes:
   - Dictámenes e informes de auditoría de la Contraloría General de la República (CGR).
   - Sentencias judiciales y resoluciones del Poder Judicial (PJUD, TRICEL, TER, Cortes).
   - Contratos, órdenes de compra y licitaciones del sistema de compras públicas (Mercado Público).
   - Decretos alcaldicios, resoluciones ministeriales y actas de concejos municipales o consejos universitarios.
   - Declaraciones Juradas de Patrimonio e Intereses (InfoProbidad / CGR).
2. **Cruce Hemerográfico:** Reconstrucción de la cronología contrastando declaraciones públicas y publicaciones de prensa para registrar lo que los actores han declarado formalmente.
3. **Regla de Oro Editorial (C.P. Scott):**
   > *«Las opiniones son libres, pero los hechos son sagrados.»*  
   > Tanto en los reportajes como en las columnas de opinión, la veracidad y precisión de los antecedentes documentales es innegociable.

---

## 🗂️ 2. Estructura del Workspace

```text
Ultimaprensa/
├── .agents/                              # Configuración de agentes autónomos y reglas de IDE
│   ├── rules/
│   │   └── metodologia_editorial.md     # Reglas permanentes de rigor y normas RAE
│   └── skills/
│       ├── ultimaprensa-reportajes/      # Metodología de reportajes de investigación
│       └── ultimaprensa-columnas/        # Metodología de columnas de opinión en 4 fases
│
├── Columnas/                             # Directorio de columnas de opinión y análisis
│   ├── README.md                         # Guía y convenciones de nombres
│   ├── guia_redaccion_columnas.md        # Manual de redacción (RAE, UDP, UniAndes LEO)
│   ├── plantilla_columna.md              # Molde estructurado para redactar
│   └── YYYY-MM-DD_titulo.md              # Archivos de columnas
│
├── reportajes/                           # Dossiers de investigación periodística
│   ├── [nombre_del_caso]/
│   │   ├── documentos/                   # PDFs originales, contratos, decretos, fallos
│   │   ├── fuentes/                      # Enlaces web y archivo de notas
│   │   ├── notas_y_datos/                # Cronologías y fichas periciales
│   │   ├── reportaje_final.md            # Reportaje en Markdown
│   │   └── reportaje_substack.html       # Exportación lista para CMS
│   │
│   └── _plantilla_reportaje/             # Molde limpio para nuevos casos
│
├── kit-journalism/                       # Toolkit oficial ultimaprensa-ia-journalism-kit
│   ├── scripts/                          # Suite de scripts y herramientas periciales
│   └── skills/                           # Skills versionados del kit
│
├── open-legal-chile/                     # Repositorio de utilidades jurídicas y leyes chilenas
└── lib/                                  # Dependencias locales para visualización de grafos
```

---

## 🛠️ 3. Toolkit de Scripts Periciales (`kit-journalism/scripts/`)

| Script | Tecnología / Motor | Propósito |
| :--- | :--- | :--- |
| **`ingestar_documentos_md.py`** | **Microsoft MarkItDown** + Poppler + OCR | Convierte PDFs, Word, Excel, PPTX e imágenes a Markdown estructurado para análisis con IA. |
| **`ocr_sentencias_pdf.py`** | **Microsoft ONNX Runtime** + RapidOCR | Extracción neuronal de texto en sentencias y expedientes judiciales escaneados. |
| **`extractor_infoprobidad.py`** | Python / Requests / BeautifulSoup | Extracción y formato imprimible de declaraciones de intereses y patrimonio (DIP). |
| **`generar_grafo_vinculos.py`** | PyVis + Vis.js + Mermaid | Trazado de redes de poder y vínculos entre personas, empresas y fondos públicos. |
| **`exportar_substack.py`** | Parser tipográfico HTML/CSS | Conversión de Markdown a HTML listo para Substack con formato corporativo. |
| **`compilador_expediente_pdf.py`** | PyMuPDF + Markdown-PDF | Compilación de denuncias y expedientes blindados con portadas A4 institucionales. |
| **`calculo_ratios_municipales.py`** | Análisis de ratios financieros | Cálculo de solvencia, liquidez y gasto en personal a honorarios municipal. |

---

## ⚡ 4. Flujo de Trabajo: Reportajes de Investigación

1. **Crear el caso:** Duplicar la plantilla en `reportajes/[nombre_del_caso]/`.
2. **Ingesta documental:**
   ```bash
   python kit-journalism/scripts/ingestar_documentos_md.py --dir reportajes/[nombre_del_caso]/documentos/ --out reportajes/[nombre_del_caso]/notas_y_datos/
   ```
3. **Cruce y Análisis:** Extraer números de decretos, montos, fechas clave y declaraciones en `cronologia_y_datos.md`.
4. **Redacción:** Redactar `reportaje_final.md` con titular de impacto sin punto final, bajada explicativa, lead, nut graf, ladillos informativos y ficha de datos.
5. **Salida Digital:**
   ```bash
   python kit-journalism/scripts/exportar_substack.py reportajes/[nombre_del_caso]/reportaje_final.md reportajes/[nombre_del_caso]/reportaje_substack.html
   ```

---

## ✍️ 5. Flujo de Trabajo: Columnas de Opinión

1. **Iniciar columna:** Crear `Columnas/YYYY-MM-DD_titulo.md` a partir de `plantilla_columna.md`.
2. **Estructura en 4 fases (Skill `ultimaprensa-columnas`):**
   * **Gancho:** Hecho detonante o actualidad que suscita la columna.
   * **Tesis:** Postura u opinión explícita, debatible y personal en los primeros párrafos.
   * **Argumentación:** Tríada de datos comprobables + causa/efecto + contraargumentación.
   * **Remate:** Cierre contundente (circular, prospectivo o ético).
3. **Extensión:** Entre **600 y 900 palabras**.
4. **Conversión y Publicación:**
   ```bash
   python kit-journalism/scripts/exportar_substack.py Columnas/YYYY-MM-DD_titulo.md Columnas/YYYY-MM-DD_titulo.html
   ```
