# Sistema de Reportajes Última Prensa: Guía Operativa y Metodología

Bienvenido al espacio de trabajo de **Última Prensa**. Esta guía detalla la metodología y el funcionamiento del sistema para crear reportajes a partir de **documentos oficiales y fuentes de prensa**.

---

## 🔍 La Metodología: Periodismo de Investigación Documental y Hemerográfico

Este enfoque de investigación (*Document-based Investigative Journalism* o *Desk Research*) es una de las ramas más rigurosas del periodismo de datos y fiscalización pública. 

### ¿En qué consiste?
1. **Evidencia Documental Primaria:** La base de cada reportaje son los documentos oficiales emitidos por organismos públicos y entidades fiscalizadas:
   - Dictámenes y auditorías de Contraloría.
   - Contratos, órdenes de compra y licitaciones del sistema de compras públicas.
   - Decretos alcaldicios, resoluciones ministeriales y actas de concejos municipales.
   - Balances financieros, memorias y registros de comercio/sociedades.
   - Resoluciones judiciales y expedientes públicos.
2. **Cruce Hemerográfico (Fuentes de Prensa):** Se revisan y contrastan las coberturas anteriores de medios de comunicación para contextualizar la cronología y registrar las **declaraciones públicas que los involucrados ya han emitido formalmente**.
3. **Sin entrevistas directas a terceros:** No se realizan entrevistas a terceros o a los implicados; toda afirmación se sostiene en la "huella documental" (*paper trail*) y en el registro público oficial.

---

## 🗂️ Estructura del Proyecto

En esta carpeta `C:\Users\Pablo\Desktop\ultimaprensa` organizaremos cada investigación de la siguiente forma:

```
ultimaprensa/
├── .agents/                    # Configuración interna del asistente
├── _plantilla_reportaje/       # Molde para duplicar en cada nuevo reportaje
│   ├── documentos/             # Coloca aquí tus PDFs, informes, contratos, balances
│   ├── fuentes/
│   │   └── enlaces_fuentes.txt # URLs de noticias y páginas web de referencia
│   ├── notas_y_datos/
│   │   └── cronologia_y_datos.md # Ficha de cruce de datos y cronología
│   └── reportaje_final.md      # El reportaje redactado y listo para publicación
├── reportajes/                 # Carpeta donde vivirán todos los reportajes creados
└── GUIA_SISTEMA_Y_METODOLOGIA.md # Este documento de referencia
```

---

## ⚡ Flujo de Trabajo Paso a Paso

### 1. Iniciar un nuevo reportaje
Solo dime en el chat: *"Iniciemos un nuevo reportaje sobre [Tema o Nombre del Caso]"*.
El asistente creará la carpeta correspondiente en `reportajes/[nombre_del_caso]/` con toda su estructura.

### 2. Cargar Insumos
- **Documentos locales:** Pega o arrastra tus archivos (PDFs, Word, Excel, informes) a la subcarpeta `reportajes/[nombre_del_caso]/documentos/`.
- **Enlaces web y notas:** Pega los links en el chat. El asistente los agregará a `reportajes/[nombre_del_caso]/fuentes/enlaces_fuentes.txt`, leerá el contenido de las páginas web y buscará fuentes públicas complementarias si hace falta.

### 3. Cruce Documental y Análisis
El asistente leerá los documentos oficiales y los artículos de prensa para:
- Extraer números de contrato, decretos, fechas y montos exactos.
- Registrar las declaraciones públicas oficiales ya emitidas por los involucrados.
- Construir la cronología de los hechos probados.

### 4. Redacción del Reportaje
El asistente generará `reportaje_final.md` aplicando el estilo de Última Prensa:
- **Titular de impacto** con verbo activo y hallazgo central.
- **Bajada explicativa** con datos duros.
- **Lead y Nut Graf** (por qué importa y qué revela el cruce de documentos).
- **Ladillos informativos** que dividen la investigación por hitos o revelaciones.
- **Cajas de datos / Destacados** con cifras clave y cronología.
- **Cierre analítico** con el estado de las investigaciones oficiales y consecuencias legales.
