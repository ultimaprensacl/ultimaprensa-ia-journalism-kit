# Generador de Portadas 4K para Instagram — Última Prensa

Herramienta oficial de generación de portadas en ultra alta resolución (4K / 2160 × 2700 px, proporción vertical 4:5) para el feed de Instagram de Última Prensa.

## Ubicación del Script
`kit-journalism/scripts/generar_portada_instagram.py`

## Especificaciones de Diseño
- **Proporción:** 4:5 vertical (feed canónico de Instagram).
- **Resolución Máster:** 2160 × 2700 px (4K / 2x Ultra HD) renderizado por Chromium Headless.
- **Badge de Marca (Top-Left):** Tarjeta marfil (`#faf7f0`) con logo de la máquina de escribir roja transparente y tipografía `Newsreader` / `Playfair Display`.
- **Tratamiento Fotográfico:** Blanco y negro de alto contraste con gradiente cálido (`sepia(20%)`, `contrast(125%)`) armónico con los tonos del logo, fundido en degradado hacia el fondo oscuro (`#141312`).
- **Sello Editorial Inclinado:** Estampilla rotada (`-4deg`) con fondo blanco, borde y tipografía terracota/coral (`#d94e34`) con tracking expandido.
- **Titular Editorial:** Tipografía serif de gran escala (`Newsreader` / `Playfair Display`) con resaltado automático en cursiva terracota/coral (`#df5844`) para palabras o cifras clave.
- **Cintillo de Sección:** Barra de acento coral con etiquetas de categoría y localidad en mayúsculas espaciadas.
- **Pie Institucional:** Llamados directos a Substack (`ultimaprensacl.substack.com`) e Instagram (`@ultimaprensa.cl`).

## Parámetros de la Línea de Comandos
```bash
python kit-journalism/scripts/generar_portada_instagram.py \
  --imagen RUTA_FOTO \
  --titular "TEXTO_DEL_TITULAR" \
  --sticker "TEXTO_ESTAMPILLA" \
  --tags "CATEGORÍA · COMUNA · REGIÓN" \
  --destacado "frase 1, frase 2" \
  --filtro {byn-calido,byn,desaturado,color} \
  --resolucion {4k,standard} \
  --vpos {25%,top,center} \
  --out RUTA_SALIDA_PNG
```

### Opciones Detalladas:
| Parámetro | Tipo | Descripción | Default |
|---|---|---|---|
| `--imagen, -i` | Obligatorio | Ruta a la fotografía de fondo (JPG, PNG). | — |
| `--titular, -t` | Obligatorio | Titular editorial de la investigación. | — |
| `--sticker, -s` | Opcional | Texto de la estampilla inclinada. | `CASO OSORNO` |
| `--sin-sticker` | Opcional | Omite por completo el sello/letrero inclinado. | `False` |
| `--tags` | Opcional | Categoría y cobertura territorial. | `INVESTIGACIÓN · OSORNO · LOS LAGOS` |
| `--destacado, -d` | Opcional | Frases o cifras a resaltar en cursiva coral. | `sin orden judicial, alta peligrosidad` |
| `--filtro` | Opcional | Tratamiento visual (`byn-calido`, `byn`, `desaturado`, `color`). | `byn-calido` |
| `--resolucion` | Opcional | `4k` (2160 × 2700 px) o `standard` (1080 × 1350 px). | `4k` |
| `--vpos` | Opcional | Posición vertical del encuadre fotográfico. | `25%` |
| `--out, -o` | Opcional | Ruta de salida del archivo PNG. Genera además `.jpg`. | `portada_instagram_4k.png` |

## Salidas Generadas
1. **Archivo PNG Máster (2160 × 2700 px):** Sin compresión con pérdida, ideal para archivo y material impreso o digital de alta fidelidad.
2. **Archivo JPG Optimizado (2160 × 2700 px, ~750 KB):** Comprimido al 95 % con optimización de tabla Huffman, listo para carga directa en Meta Business Suite o Instagram sin exceder límites de peso.
