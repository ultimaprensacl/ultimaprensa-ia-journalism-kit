# 📰 Última Prensa IA Journalism Kit
### *Framework de Periodismo de Investigación Documental y Fiscalización Pública Asistido por Inteligencia Artificial*

> **Desarrollado por [Última Prensa](https://ultimaprensa.cl) en colaboración con la tecnología de Gemini de Google y los estándares de verificación de la Associated Press (AP).**

---

## 📌 1. Visión y Propósito

El **Última Prensa IA Journalism Kit** es un entorno de trabajo y conjunto de herramientas metodológicas diseñadas para estructurar, auditar, investigar y redactar reportajes de **periodismo de fiscalización y datos públicos**, apoyado por modelos avanzados de Inteligencia Artificial (**Gemini / Antigravity**) bajo estrictos controles éticos y lingüísticos.

Este framework permite a salas de redacción, periodistas independientes e investigadores procesar miles de páginas de expedientes oficiales, detectar irregularidades contables complejas, construir cronologías judiciales inexpugnables y traducir indicadores técnicos a un lenguaje claro y de alto impacto para la ciudadanía.

---

## 🔍 2. Metodología: Periodismo Documental y Desk Research

El sistema se basa en el principio de **Evidencia Documental Primaria (*Paper Trail*)**:

1. **La Huella Oficial:** La investigación no se sustenta en rumores, filtraciones anónimas o trascendidos. La columna vertebral son los documentos públicos vinculantes:
   - Dictámenes y sumarios administrativos de la Contraloría General de la República (CGR).
   - Sentencias de tribunales ordinarios y especiales (TRICEL, TER, Cortes de Apelaciones, Corte Suprema).
   - Licitaciones, órdenes de compra y contratos de Mercado Público.
   - Balances presupuestarios, decretos alcaldicios y actas de concejos municipales.
2. **Cruce Hemerográfico:** Reconstrucción de la cronología mediante la revisión exhaustiva de fuentes de prensa y declaraciones oficiales emitidas previamente por los involucrados.
3. **Cero Adjetivación / Foco en los Hechos:** Los datos duros, las fechas y los montos exactos son los protagonistas narrativos.

---

## ⚖️ 3. Estándares Editoriales y Deontológicos

### A. Estándares Associated Press (AP) y Fact-Checking
* **Verificación de Origen:** Todo dato debe contar con atribución precisa (número de oficio, fecha, tribunal o balance).
* **Contexto Estadístico y Per Cápita:** Prohibición de publicar cifras millonarias o porcentajes aislados sin traducirlos a su impacto relativo comunal (e.g., costo por habitante o equivalencia en obras públicas).
* **Equilibrio y Derecho a Réplica:** Registro transparente de las declaraciones oficiales y versiones de descargo de las personas o entidades aludidas.

### B. Normas de la RAE para Periodismo Digital
* **Titulares y Bajadas:** Sin punto final de cierre (según norma RAE para enunciados aislados).
* **Verbos Asertivos:** Erradicación del condicional de rumor (*"habría defraudado"*) para hechos plenamente acreditados en sentencias y auditorías ejecutoriadas.
* **Nombres Periodísticos Ágiles:** Uso de nombre y apellido principal, evitando saturación de nombres triples notariales.

### C. Protocolo de Inteligencia Artificial
* **Cero Redundancia:** Cada bloque del reportaje aporta hechos o evidencias nuevas.
* **Enriquecimiento Progresivo:** La IA no resume ni poda datos técnicos esenciales; complementa y contextualiza.
* **Depuración de Elementos Superfluos:** Supresión de ramas accesorias que desvíen el foco de la investigación.

---

## 🗂️ 4. Estructura del Repositorio

```text
ultimaprensa-ia-journalism-kit/
│
├── .agents/
│   └── rules/
│       └── metodologia_documental.md     # Reglas permanentes del asistente de IA
│
├── skills/
│   └── ultimaprensa-reportajes/          # Skill de redacción, escaletas y estilos
│       ├── SKILL.md                      # Instrucciones maestras del skill
│       ├── references/
│       │   ├── verificacion_ap_y_transparencia.md # Guía AP y análisis de datos
│       │   ├── manual_estilo.md                   # Normas RAE y estilo editorial
│       │   └── plantillas.md                      # Moldes estructurales de reportajes
│       └── examples/
│           └── ejemplo_reportaje.md               # Caso modelo de referencia
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
├── scripts/                              # Herramientas de automatización y cálculo
│   ├── ocr_sentencias_pdf.py             # OCR neuronal (RapidOCR) para fallos escaneados
│   └── calculo_ratios_municipales.py     # Calculadora de solvencia y pérdida per cápita
│
├── GUIA_SISTEMA_Y_METODOLOGIA.md         # Manual operativo del sistema
├── .gitignore                            # Filtro para mantener privados los casos de trabajo
└── README.md                             # Este manual institucional
```

---

## 🛠️ 5. Herramientas y Scripts Incluidos

### 1. Extractor OCR de Fallos y Dictámenes Escaneados (`scripts/ocr_sentencias_pdf.py`)
Permite procesar expedientes judiciales de cientos de páginas escaneadas (CGR, TRICEL o Juzgados) mediante OCR neuronal local:
```bash
python scripts/ocr_sentencias_pdf.py ruta/al/expediente.pdf salida_texto.txt
```

### 2. Calculadora de Ratios e Impacto Per Cápita (`scripts/calculo_ratios_municipales.py`)
Calcula el índice de liquidez corriente y genera automáticamente las equivalencias en obras sociales (postas rurales, ambulancias, pavimentación):
```bash
python scripts/calculo_ratios_municipales.py
```

---

## 🚀 6. Flujo de Trabajo para Nuevas Investigaciones

1. **Crear el caso:** Duplicar la carpeta `_plantilla_reportaje/` con el nombre del caso (ej. `reportajes/caso_empresa_electrica/`).
2. **Cargar insumos:**
   - Colocar los informes PDF en `documentos/`.
   - Agregar las URLs de prensa en `fuentes/enlaces_fuentes.txt`.
3. **Auditoría con el Asistente:**
   - La IA lee los archivos, ejecuta el OCR si son escaneados y extrae números de decretos, montos y fechas en `notas_y_datos/cronologia_y_datos.md`.
4. **Redacción Estructurada:**
   - Generación de `reportaje_final.md` con:
     - Titular de impacto y bajada explicativa.
     - Lead y Nut Graf (*Tuerca de la historia*).
     - Ficha pericial y Guía ciudadana.
     - Ladillos temáticos de evidencia.
     - Cierre analítico y nota metodológica de transparencia.

---

## 🔒 7. Privacidad y Seguridad

Por defecto, este repositorio incluye un archivo `.gitignore` estricto configurado para que **todos los documentos, audios de entrevistas, imágenes y carpetas individuales de investigación permanezcan 100% locales y privados**, asegurando que solo el framework y las herramientas reutilizables se sincronicen con el repositorio remoto.

---

## 🤝 8. Créditos y Transparencia

Este framework es una iniciativa de periodismo tecnológico desarrollada por el equipo de **[Última Prensa](https://ultimaprensa.cl)** en alianza con la tecnología de **Gemini de Google**.

* **Dirección Editorial:** Equipo de Periodismo de Investigación de Última Prensa.
* **Licencia:** MIT (Herramientas y Framework de libre uso para el fortalecimiento del periodismo de fiscalización).
