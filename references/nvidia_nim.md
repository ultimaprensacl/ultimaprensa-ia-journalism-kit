# Modelos NVIDIA NIM en Última Prensa

Guía del router `scripts/nvidia_router.py`: qué modelos de NVIDIA se usan para
cada tarea del reportaje, cuánto se permite de cada uno y cómo se responde
cuando un modelo se queda sin cupo.

## Estado al 25 de octubre de 2026

Verificado funcionando:

- Clave de NVIDIA guardada en `kit-journalism/.env` y `~/.hermes/.env` (permisos
  600), con inferencia real confirmada.
- Router con 8 tareas NVIDIA + 2 motores CLI (`claude`, `agy`).
- Pruebas reales: bajada y titulares con Nemotron 3 Ultra, apertura con
  Claude Opus 5.5 y con Gemini 4 Argon, embeddings de 2048 dimensiones,
  `pase_completo` con Opus.
- Autoprueba del router 16/16 y suite del kit 8/8.

Pendiente:

- Revocar las dos claves de NVIDIA que quedaron escritas en el chat.
- Probar la cadena completa sobre un reportaje entero, para medir el consumo
  real por reportaje (hoy el cálculo de 1,5 millones de tokens es estimación).

---

## 1. Cómo se cobra (verificado en octubre de 2026)

| Dato | Valor |
|---|---|
| Endpoint | `https://integrate.api.nvidia.com/v1` (compatible con la API de OpenAI) |
| Costo del trial | **Cero, sin tarjeta de crédito** |
| Límite del trial | Por peticiones por minuto: alrededor de **40 RPM** por modelo |
| Cobro por token en el trial | **No existe** |
| Sistema de créditos | Retirado en septiembre de 2025; hoy solo hay límites de tasa |
| Catálogo | 85 modelos en `/v1/models`, más NIM de voz que van por gRPC |

NVIDIA dejó de usar créditos: la respuesta oficial en su foro es que el sistema
de créditos «ha sido reemplazado por límites de tasa para uso de prueba». Es
decir, las «1.000 créditos» que muestra la cuenta no son un saldo que se
consuma ni que haya que recargar. Lo que se agota es el ritmo de peticiones.

Para tener más caudal hay dos caminos, y ninguno hace falta hoy:

1. **Autohospedar** el contenedor NIM en una GPU propia (se paga la GPU, no los tokens).
2. **Partner endpoint** (Together, Fireworks, DeepInfra, etc.), que sí cobra por token.

Como referencia de ese segundo camino, Nemotron 3 Ultra se ha publicado en
torno a **USD 0,50–0,90 por millón de tokens de entrada y 1,70–3,60 de salida**.
Para comparar: Gemini 3.8 Flash cuesta hoy **0,75 / 3,75** por millón (sube a
1,50 / 7,50 el 1 de enero de 2027).

> Conclusión práctica: **no hay nada que pagar**. Si algún día el volumen supera
> el trial, primero se mide con `nvidia_router.py estado` y recién después se decide.

---

## 2. Qué modelo hace qué en el proyecto

Los identificadores están verificados contra el catálogo real del endpoint **y
sondeados uno por uno contra la cuenta**: el catálogo lista modelos que la
cuenta no tiene habilitados.

| Tarea | Modelos (en orden de respaldo) | Para qué |
|---|---|---|
| `redaccion` | `nvidia/nemotron-3-ultra-550b-a55b` → `z-ai/glm-5.3` → `deepseek-ai/deepseek-v4.1-flash` | Escribir y editar reportajes, columnas y titulares |
| `analisis_largo` | `nvidia/nemotron-3-ultra-550b-a55b` → `deepseek-ai/deepseek-v4.1-flash` | Dossiers y expedientes completos (contexto de 1M) |
| `extraccion` | `nvidia/nemotron-3-ultra-550b-a55b` → `z-ai/glm-5.3` | Sacar datos duros sin creatividad (temperatura 0) |
| `verificacion` | `nvidia/nemotron-3-ultra-550b-a55b` → `z-ai/glm-5.3` | Contraste de afirmaciones y contradicciones |
| `ideas` | `nvidia/nemotron-3-ultra-550b-a55b` → `z-ai/glm-5.3-flash` | Ángulos, hipótesis y preguntas de investigación |
| `clasificar` | `nvidia/nemotron-3-ultra-550b-a55b` → `z-ai/glm-5.3-flash` | Triage masivo de documentos |
| `embeddings` | `nvidia/nemotron-3-embed-1b` → `nvidia/nemotron-3.5-embed-1b` | Búsqueda semántica y RAG (2048 dimensiones) |
| `documentos` | `nvidia/nemotron-parse-2.0` | Texto, tablas y estructura de páginas escaneadas |

### Lo que la cuenta no tiene habilitado

`moonshotai/kimi-k2.6` y `nvidia/nemotron-nano-3-30b-a3b` aparecen en el
catálogo pero devuelven **404 `Not found for account`**. Se probaron y se
sacaron del reparto; volver a probarlos antes de reincorporarlos.

### Latencias medidas (octubre 2026)

| Modelo | Respuesta corta |
|---|---|
| `nemotron-parse-2.0` | 1 s |
| `nemotron-3-ultra-550b-a55b` | 2 s (y ~19 s para una bajada de 40 palabras) |
| `z-ai/glm-5.3` | 12 s |
| `z-ai/glm-5.3-flash` | 92 s |
| `deepseek-ai/deepseek-v4.1-flash` | intermitente: de 4 s a más de 150 s |

Por eso Ultra, que además es el más capaz, es el caballo de batalla y lleva el
cupo más alto. El `timeout_s` de la configuración está en 240 s justamente por
DeepSeek.

### El razonamiento se come los tokens

DeepSeek y glm-flash razonan por defecto. Con `max_tokens` bajo, todo el
presupuesto se gasta en el razonamiento y el campo `content` vuelve **nulo**
(el texto queda en `reasoning_content`). El router lo detecta, devuelve lo que
haya y avisa «sube --max-tokens». Para tareas cortas, `--max-tokens 700` es un
piso razonable.

### Embeddings: dos modelos, dos contratos

`nemotron-3.5-embed-1b` es asimétrico y **exige** `input_type`; sin él responde
400. `nemotron-3-embed-1b` funciona con o sin el campo, y por eso va primero.

---

## 3. Cuotas: el «cuánto» de cada modelo

Cada modelo tiene su propio techo, en `config/nvidia.yaml`:

```yaml
limites:
  rpm_global: 30            # margen bajo el techo real de ~40 RPM
  llamadas_dia: 1500        # tope propio de seguridad
  por_modelo:
    nvidia/nemotron-3-ultra-550b-a55b: {rpm: 4, dia: 150}
    deepseek-ai/deepseek-v4.1-flash:   {rpm: 10, dia: 600}
```

Qué pasa cuando un modelo se queda sin cupo:

1. El router lo descarta para el resto de la ejecución y **pasa al siguiente
   candidato de la tarea**, sin intervención.
2. La llamada queda anotada en `.nvidia_router/uso.json` (contador diario, que
   se reinicia solo a medianoche).
3. Si todos los candidatos están sin cupo, el comando devuelve error y explica
   cuál fue el motivo de cada intento, en vez de fallar en silencio.

Para subir o bajar el caudal de un modelo, se edita `rpm` o `dia` y listo: no
hay que tocar el código.

---

## 4. Uso

### Guardar la clave una sola vez

```bash
bash kit-journalism/scripts/configurar_nvidia_key.sh
```

Pide la clave con la entrada oculta, la guarda en `kit-journalism/.env` y en
`~/.hermes/.env` con permisos 600, y verifica con una inferencia mínima que
funcione de verdad. La clave se genera gratis en
<https://build.nvidia.com/settings/api-keys>.

### Comandos

```bash
# Cupos, uso del día y control de que los modelos configurados existan
python kit-journalism/scripts/nvidia_router.py estado

# Catálogo real del endpoint (no necesita clave)
python kit-journalism/scripts/nvidia_router.py modelos

# Una tarea editorial, con el texto directo o desde archivo
python kit-journalism/scripts/nvidia_router.py llamar --tarea redaccion --archivo nota.md
python kit-journalism/scripts/nvidia_router.py llamar --tarea extraccion --texto "..." --json

# Instrucción de sistema propia y límites por llamada
python kit-journalism/scripts/nvidia_router.py llamar --tarea verificacion \
  --sistema "Eres editor de investigación; no inventes datos" \
  --archivo borrador.md --max-tokens 4000

# Embeddings por lotes
python kit-journalism/scripts/nvidia_router.py embeddings --texto "fragmento uno" --texto "fragmento dos"

# Autoprueba completa, sin red ni clave (servidor NVIDIA simulado)
python kit-journalism/scripts/nvidia_router.py --autoprueba
```

### Desde Python

```python
import sys
sys.path.insert(0, "kit-journalism/scripts")
from nvidia_router import RouterNVIDIA

router = RouterNVIDIA()
resultado = router.chat("verificacion", [
    {"role": "system", "content": "Contrasta cada afirmación contra la fuente citada."},
    {"role": "user", "content": texto},
])
print(resultado["modelo"], resultado["uso"])   # modelo que respondió y consumo
print(resultado["texto"])
```

### Desde Hermes

Hay tres alias ya configurados para conversar directamente con estos modelos:

```
/model nemotron     # nvidia/nemotron-3-ultra-550b-a55b
/model nvflash      # deepseek-ai/deepseek-v4.1-flash
/model nvglm        # z-ai/glm-5.3
```

`/model nemotron --global` lo deja como modelo por defecto de todas las sesiones.

---

## 5. El pase final va por CLI, no por API

El reparto general del trabajo es este:

| Etapa | Motor | Por qué |
|---|---|---|
| Leer expedientes, extraer datos, clasificar, verificar contra corpus, embeddings | NVIDIA NIM (trial) | Gratis, contexto de 1M y responde en 2 s: es donde el volumen no se puede pagar |
| Apertura, titular, riesgo legal, pase final | Claude Code (Opus/Sonnet) | Criterio editorial; la cuota Opus es la más amplia que tenés |
| Segunda opinión o respaldo cuando la cuota de Claude se agota | Antigravity (Argon / 3.8 Flash) | Grupo de cuota distinto, sin costo por token |

Para el trabajo donde importa la calidad de la prosa no hace falta pagar Opus ni
Argon por token: los CLIs de agente usan los planes que ya tienes.

```bash
python kit-journalism/scripts/nvidia_router.py derivar --motor agy --tarea titular \
  --archivo reportajes/caso_x/borderador.md --workdir reportajes/caso_x
```

Tareas disponibles: `apertura`, `titular`, `riesgo_legal`, `pase_final`. La
instrucción de cada una vive en `config/nvidia.yaml` (sección `derivacion`) y se
puede reemplazar con `--instruccion "..."`.

Cómo funciona: el material se escribe en `.derivacion_<tarea>.md` dentro del
workdir y el CLI recibe la orden de leerlo. Así no se choca con el límite de
longitud de argumentos y el agente puede usar su propia lectura de archivos.
La derivación queda en el mismo registro de uso que las llamadas a la API, con
el prefijo `cli:` en el nombre del modelo.

Modelos que entrega Antigravity hoy con el plan AI Pro (`agy models`):
`claude-opus-5-5-{low,medium,high}`, `claude-sonnet-5-5-{low,medium,high}`,
`gemini-4-argon-{low,medium,high}`, `gemini-3.8-flash-{low,medium,high}`,
`gpt-oss-120b-medium`. Los modelos Claude y los Gemini **tienen cuotas
separadas**: si una se agota, la otra sigue disponible.

### Reparto final por tarea

Claude es el motor principal (tiene más cuota Opus); Antigravity es la segunda
opinión y el respaldo cuando la cuota de Claude está agotada.

| Tarea | Claude | Esfuerzo | Antigravity | Esfuerzo |
|---|---|---|---|---|
| `apertura` | `opus` (claude-opus-5-5) | `medium` | `gemini-4-argon-high` | en el nombre |
| `titular` | `sonnet` (claude-sonnet-5-5) | `low` | `gemini-3.8-flash-high` | en el nombre |
| `riesgo_legal` | `opus` | `high` | `gemini-4-argon-high` | en el nombre |
| `pase_final` | `opus` | `high` | `gemini-4-argon-high` | en el nombre |

El criterio del esfuerzo: `low` para lo mecánico y de bajo riesgo (cinco
titulares), `medium` para la prosa —escribir bien es criterio, no cómputo— y
`high` donde el error tiene consecuencia legal o factual.

### Medición con el mismo material

Apertura del reportaje de Curaco, misma instrucción, los dos motores:

| Motor | Tiempo | Tokens | Resultado |
|---|---|---|---|
| Claude `opus` @medium | 21 s | 70.653 | Cinco párrafos, cita textual de «técnicamente apto», peritajes identificados por nombre |
| `agy` Argon high | 57 s | 16.911 | Tres párrafos, mismo hecho, más compacto |

Claude tarda un tercio y entrega más detalle específico; Antigravity gasta una
cuarta parte de los tokens. Con cuota de Claude amplia, el orden correcto es
Claude primero.

Cada motor informa el consumo a su manera (`agy` trae `total_tokens`; `claude`
separa entrada fresca, caché y salida) y el router lo normaliza. El
`total_cost_usd` que reporta Claude Code es el costo teórico a tarifa de API:
con plan Pro no se cobra, pero sirve como medida de cuánta cuota consumió.

## 6. Lo que este catálogo no trae

- **Transcripción y voz sintética por HTTP**: los NIM de voz (Parakeet,
  Canary, Magpie TTS) no aparecen en `/v1/models` porque se sirven por gRPC
  (`grpc.nvcf.nvidia.com`). No se integraron: el kit ya resuelve ambas cosas
  sin conexión, con `transcribir_audio_investigacion.py` (faster-whisper) y
  `generar_podcast_investigacion.py` (Kokoro y voces neuronales).
- **Costo por token**: en el trial no existe. No hay factura que controlar.
- **Metadatos de contexto**: `/v1/models` devuelve solo `id` y `owned_by`; la
  ventana de contexto hay que consultarla en la ficha de cada modelo.
