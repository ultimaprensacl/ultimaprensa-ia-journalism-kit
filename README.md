# 📰 Última Prensa IA Journalism Kit
### *Framework Universal de Periodismo de Investigación Documental, Fiscalización Pública y Columnas de Opinión Asistido por Inteligencia Artificial*

> **Desarrollado por [Última Prensa](https://ultimaprensa.cl) en colaboración con la tecnología de Gemini de Google y los estándares de verificación de la Associated Press (AP).**
>
> 🚀 **Compatibilidad Universal:** Diseñado para operar con cualquier CLI o entorno de IA: **Google Antigravity (`agy`)**, **Claude Code CLI (`claude`)**, **Codex / OpenAI CLI**, **Hermes**, **OpenCode**, **Cursor**, **Windsurf** y **Aider**.

---

## 📌 1. Visión y Propósito

El **Última Prensa IA Journalism Kit** es un entorno de trabajo y conjunto de herramientas metodológicas diseñadas para estructurar, auditar, investigar y redactar reportajes de **periodismo de fiscalización y datos públicos**, así como **columnas de opinión y análisis crítico**, apoyado por modelos avanzados de Inteligencia Artificial bajo estrictos controles éticos y lingüísticos.

Este framework permite a salas de redacción, periodistas independientes e investigadores procesar miles de páginas de expedientes oficiales, detectar irregularidades contables complejas, construir cronologías judiciales inexpugnables, trazar mapas de redes de poder y traducir indicadores técnicos a un lenguaje claro y de alto impacto para la ciudadanía.

---

## 🤖 2. Compatibilidad Multi-CLI y Agentes de IA

El repositorio incluye archivos de configuración nativos para los principales ecosistemas de agentes de IA:

| Asistente / CLI | Archivo de Configuración | Comando / Uso |
| :--- | :--- | :--- |
| **Google Antigravity / Gemini** | `GEMINI.md` / `.agents/rules/` / `skills/` | Nativo en Antigravity IDE y CLI `agy` |
| **Claude Code CLI** | `CLAUDE.md` | `claude` (Anthropic Claude Code) |
| **Codex / OpenAI CLI** | `AGENTS.md` | Universal Codex / ChatGPT CLI |
| **Hermes / OpenCode / Aider** | `AGENTS.md` | Compatible con agentes de terminal abiertos |
| **Cursor / Windsurf / Copilot** | `AGENTS.md` / `.agents/rules/` | Soporte de reglas contextuales de IDE |

---

## 🔍 3. Metodología: Periodismo Documental y Desk Research

El sistema se basa en el principio de **Evidencia Documental Primaria (*Paper Trail*)**:

1. **La Huella Oficial:** La investigación no se sustenta en rumores o filtraciones anónimas. La base son los documentos públicos vinculantes:
   - Dictámenes y sumarios administrativos de la Contraloría General de la República (CGR).
   - Sentencias de tribunales ordinarios y especiales (PJUD, TRICEL, TER, Cortes de Apelaciones, Corte Suprema).
   - Licitaciones, órdenes de compra y contratos de Mercado Público.
   - Balances presupuestarios, decretos alcaldicios y actas de concejos municipales.
   - Declaraciones Juradas de Patrimonio e Intereses (InfoProbidad / CGR).
2. **Cruce Hemerográfico:** Reconstrucción de la cronología mediante la revisión exhaustiva de fuentes de prensa y declaraciones oficiales emitidas previamente por los involucrados.
3. **Cero Adjetivación / Foco en los Hechos:** Los datos duros, las fechas y los montos exactos son los protagonistas narrativos.
4. **Regla de Oro en Opinión (C.P. Scott):** *«Las opiniones son libres, pero los hechos son sagrados»*. Las columnas de análisis descansan sobre premisas fácticas contrastables.

---

## ⚖️ 4. Estándares Editoriales y Deontológicos

### A. Estándares Associated Press (AP) y Fact-Checking
* **Verificación de Origen:** Todo dato debe contar con atribución precisa (número de oficio, fecha, tribunal o balance).
* **Contexto Estadístico y Per Cápita:** Prohibición de publicar cifras millonarias o porcentajes aislados sin traducirlos a su impacto relativo comunal (e.g., costo por habitante o equivalencia en obras públicas).
* **Equilibrio y Derecho a Réplica:** Registro transparente de las declaraciones oficiales y versiones de descargo de las personas o entidades aludidas.

### B. Normas de la RAE para Periodismo Digital
* **Titulares y Bajadas:** Sin punto final de cierre (según norma RAE para enunciados aislados).
* **Tipografía de Citas:** Citas textuales entre comillas latinas o angulares (« »).
* **Verbos Asertivos:** Erradicación del condicional de rumor (*"habría defraudado"*) para hechos plenamente acreditados en sentencias y auditorías ejecutoriadas.
* **Nombres Periodísticos Ágiles:** Uso de nombre y apellido principal, evitando saturación de nombres triples notariales.

### C. Protocolo de Inteligencia Artificial
* **Cero Redundancia:** Cada bloque del reportaje aporta hechos o evidencias nuevas.
* **Enriquecimiento Progresivo:** La IA no resume ni poda datos técnicos esenciales; complementa y contextualiza.
* **Depuración de Elementos Superfluos:** Supresión de ramas accesorias que desvíen el foco de la investigación.

---

## 🗂️ 5. Estructura del Repositorio

```text
ultimaprensa-ia-journalism-kit/
│
├── AGENTS.md                             # Configuración universal para Codex, Hermes, OpenCode
├── CLAUDE.md                             # Configuración nativa para Claude Code CLI
├── GEMINI.md                             # Configuración nativa para Gemini / Antigravity
│
├── .agents/
│   └── rules/
│       └── metodologia_documental.md     # Reglas permanentes de rigor e investigación
│
├── skills/
│   ├── ultimaprensa-reportajes/          # Skill de reportajes de investigación a fondo
│   │   ├── SKILL.md
│   │   ├── references/                   # Manual de estilo, normas AP y plantillas
│   │   └── examples/                     # Reportaje modelo
│   │
│   └── ultimaprensa-columnas/            # Skill de columnas de opinión y análisis
│       └── SKILL.md                      # Estructura canónica en 4 fases y normas RAE
│
├── _plantilla_reportaje/                  # Molde limpio para iniciar nuevas investigaciones
│   ├── documentos/                       # Espacio para PDFs, contratos y balances
│   │   └── .gitkeep
│   ├── fuentes/                          # Registro de enlaces web de consulta
│   │   └── enlaces_fuentes.txt
│   ├── notas_y_datos/                    # Fichas de cruce y cronologías
│   │   └── cronologia_y_datos.md
│   └── reportaje_final.md                # Plantilla base estructurada
│
├── scripts/                              # Suite de automatización, peritaje y publicación
│   ├── ingestar_documentos_md.py         # Conversor universal a MD (Microsoft MarkItDown + OCR)
│   ├── ocr_sentencias_pdf.py             # OCR neuronal (RapidOCR + Microsoft ONNX Runtime)
│   ├── ocr_paddle.py                     # OCR neuronal avanzado de alta resolución (PaddleOCR)
│   ├── extractor_infoprobidad.py         # Extractor integral de declaraciones de patrimonio (DIP)
│   ├── investigacion_chile_mcp.py        # Servidor MCP de datos públicos (Mercado Público, DIP, CGR, FTM)
│   ├── generar_grafo_vinculos.py         # Generador de grafos (Mermaid, HTML/Vis.js y FollowTheMoney)
│   ├── exportar_substack.py              # Exportador a HTML enriquecido y justificado para Substack
│   ├── publicar_substack_n8n.py          # Conector automatizado hacia Substack vía n8n webhook
│   ├── compilador_expediente_pdf.py      # Ensamblador de expedientes blindados con portadas A4
│   ├── calculo_ratios_municipales.py     # Calculadora financiera de balances y honorarios municipales
│   ├── rae_client.py                     # Cliente pericial de la API oficial de la RAE
│   ├── rae_mcp_server.py                 # Servidor Model Context Protocol para auditoría léxica RAE
│   ├── servidor_datasette.py             # Motor web interactivo SQL para bases de datos periciales
│   └── test_e2e_toolkit.py               # Suite de verificación y pruebas automatizadas End-to-End
│
├── .env.example                          # Plantilla de credenciales y variables de entorno
├── GUIA_SISTEMA_Y_METODOLOGIA.md         # Manual operativo del sistema
├── .gitignore                            # Filtro de privacidad estricto para investigaciones
└── README.md                             # Este manual institucional
```

---

## 🛠️ 6. Herramientas y Scripts Incluidos

### 1. Ingestor Universal de Documentos a Markdown (`scripts/ingestar_documentos_md.py`)
Convierte automáticamente expedientes, contratos, decretos, planillas y presentaciones a **Markdown limpio y estructurado**, permitiendo al modelo de IA procesar la evidencia sin pérdida de contexto:
- **Motor principal:** Librería oficial **MarkItDown de Microsoft** (`microsoft/markitdown`) para PDFs, Word (`.docx`), Excel (`.xlsx`), PowerPoint (`.pptx`) e imágenes.
- **Modo híbrido y Fallback:** Extrae mediante Poppler (`pdftotext`) y aplica OCR (`tesseract`) si el documento carece de capa digital de texto:
```bash
# Ingestar un directorio completo de documentos:
python scripts/ingestar_documentos_md.py --dir ruta/a/documentos/ --out salida_md/

# Ingestar un archivo específico con OCR forzado:
python scripts/ingestar_documentos_md.py --file fallo_escaneado.pdf --out salida_md/ --ocr
```

### 2. Extractor OCR Neuronal de Sentencias (`scripts/ocr_sentencias_pdf.py` y `scripts/ocr_paddle.py`)
Procesa sentencias judiciales y dictámenes escaneados de cientos de fojas utilizando inferencia neuronal con **Microsoft ONNX Runtime** + `RapidOCR` o `PaddleOCR`:
```bash
python scripts/ocr_sentencias_pdf.py expediente_pjud.pdf salida_texto.txt
```

### 3. Extractor de Patrimonio e Intereses de InfoProbidad (`scripts/extractor_infoprobidad.py`)
Descarga y desglosa íntegramente las Declaraciones de Patrimonio e Intereses (DIP) de autoridades públicas desde InfoProbidad.cl (por URL o por ID de declaración), superando pestañas colapsadas y generando Markdown, JSON y un HTML imprimible de alta fidelidad:
```bash
python scripts/extractor_infoprobidad.py "https://www.infoprobidad.cl/Declaracion/BuscarDeclaracion?declaracion=HASH_O_ID"
```

### 4. Generador de Grafos y Estándar FollowTheMoney (`scripts/generar_grafo_vinculos.py`)
Construye mapas relacionales entre autoridades, sociedades, inmuebles, decretos y montos públicos. Exporta simultáneamente a **Mermaid**, **HTML interactivo** (PyVis) y **FollowTheMoney JSONL** (OCCRP / Aleph):
```bash
python scripts/generar_grafo_vinculos.py --data vinculos.json --out-html grafo.html --out-md grafo.md --out-ftm grafo.ftm.jsonl
```

### 5. Servidor MCP de Datos Públicos e Investigación (`scripts/investigacion_chile_mcp.py`)
Servidor Model Context Protocol que otorga a los agentes de IA capacidad de consultar de forma autónoma:
- Búsqueda de licitaciones y órdenes de compra en Mercado Público / ChileCompra.
- Consulta de contratistas del Estado y validación de RUT.
- Extracción de declaraciones DIP de InfoProbidad.
- Búsqueda de jurisprudencia y dictámenes de la Contraloría General de la República (CGR).
- Generación de entidades FollowTheMoney (*Person, Company, Contract, PublicBody*).

### 6. Conversor y Publicador a Substack (`scripts/exportar_substack.py` y `scripts/publicar_substack_n8n.py`)
Transforma artículos a HTML optimizado para Substack con estricta justificación tipográfica (`text-align: justify;`), citas en bloque enriquecidas y cintillo institucional. Permite publicación directa o vía flujos de n8n:
```bash
python scripts/exportar_substack.py reportaje_final.md reportaje_substack.html
python scripts/publicar_substack_n8n.py --archivo reportaje_substack.html --modo n8n
```

### 7. Compilador de Expedientes Blindados en PDF (`scripts/compilador_expediente_pdf.py`)
Ensambla escritos judiciales o denuncias en Markdown junto con todos sus anexos probatorios en PDF, intercalando portadas A4 institucionales con numeración y descripción de cada anexo:
```bash
python scripts/compilador_expediente_pdf.py --md escrito_denuncia.md --salida expediente_blindado.pdf
```

### 8. Calculadora de Ratios Municipales (`scripts/calculo_ratios_municipales.py`)
Calcula el índice de solvencia, liquidez corriente y sobregasto de personal a honorarios en auditorías municipales, traduciéndolo a pérdida per cápita y equivalencias comunitarias (*postas, ambulancias, pavimento*):
```bash
python scripts/calculo_ratios_municipales.py --comuna Osorno --poblacion 173000 --caja 4500000000 --pasivos 3200000000 --honorarios 850000000 --gastos-personal 3200000000
```

### 9. Explorador SQL de Bases de Datos con Datasette (`scripts/servidor_datasette.py`)
Levanta una interfaz web interactiva para auditar bases de datos forenses locales (SQLite y DuckDB) sin requerir instalación compleja:
```bash
python scripts/servidor_datasette.py investigacion.db --port 8005
```

### 10. Suite de Verificación End-to-End (`scripts/test_e2e_toolkit.py`)
Auditoría y prueba automatizada de todo el toolkit para asegurar que cada herramienta opere al 100 %:
```bash
python scripts/test_e2e_toolkit.py
```

---

## ✍️ 7. Módulo de Columnas de Opinión

Para el análisis ágil de la contingencia, el kit incorpora el skill `ultimaprensa-columnas` y el subagente especializado `columnista_opinion`, con una estructura en 4 fases:

1. **Gancho:** Hecho detonante o acontecimiento de actualidad.
2. **Tesis:** Postura u opinión unívoca, explícita y debatible en los primeros párrafos.
3. **Tríada Argumentativa:** Datos/evidencia documental + Causalidad (costo social/institucional) + Refutación de contraargumento.
4. **Remate:** Cierre contundente (circular, prospectivo o interrogante ética).

Extensión: **600 a 900 palabras**.

---

## 🔒 8. Privacidad y Seguridad

Por defecto, este repositorio incluye un archivo `.gitignore` estricto configurado para que **todos los documentos, audios de entrevistas, imágenes y carpetas individuales de investigación permanezcan 100% locales y privados**, asegurando que solo el framework y las herramientas reutilizables se sincronicen con el repositorio remoto.

---

## 🤝 9. Créditos y Transparencia

Este framework es una iniciativa de periodismo tecnológico desarrollada por el equipo de **[Última Prensa](https://ultimaprensa.cl)** en alianza con la tecnología de **Gemini de Google**.

* **Dirección Editorial:** Equipo de Periodismo de Investigación de Última Prensa.
* **Licencia:** MIT (Herramientas y Framework de libre uso para el fortalecimiento del periodismo de fiscalización).
