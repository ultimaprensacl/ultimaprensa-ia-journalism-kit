# Flujo editorial

Una pieza por encargo: **el editor da el tema y el ciclo arranca**. No hay horario
fijo ni cadencia automática; el formato lo define el encargo (nota corta o reportaje
grande), no el día de la semana. El borrador queda en disco con su control de calidad
pasado; la firma y la publicación son del editor.

## Las piezas

| Pieza | Dónde vive | Quién la provee |
|---|---|---|
| Tema y ángulo | el chat, o `reportajes/_agenda/AAAA-MM-DD.md` | El editor |
| Andamiaje y control | `kit-journalism/scripts/pipeline_editorial.py` | Script: abre, marca etapas, lanza el pase, corre QA, cierra |
| Procedimiento | skill `ultimaprensa-diario` | Hermes |
| Radar matinal | cron `bf4c6c24196c` — **pausado** | Opcional, se reactiva si se quiere |

## Arranque

Con el tema por delante, un solo comando abre todo:

```bash
cd ~/Escritorio/Ultimaprensa
kit-journalism/.venv/bin/python kit-journalism/scripts/pipeline_editorial.py abrir \
  --tema "Relleno de Curaco: la indemnización a Servitrans" --tipo nota
```

Crea la agenda del día si no existe, el expediente en `reportajes/<fecha>_<slug>/`
con `brief.md` y `estado.json`, y deja la primera etapa marcada. Si ya hay una agenda
escrita a mano, `abrir` sin argumentos la lee.

## Etapas

| Etapa | Producto | Quién |
|---|---|---|
| `agenda` | `brief.md` | script |
| `cobertura` | `cobertura.md` — matriz de medios: qué publicó cada uno, cuándo, con qué fuente y qué dato nuevo aporta | agente (web) |
| `legal` | `legal.md` — norma aplicable, quién fiscaliza e informes ya emitidos (CGR, SMA, SII, CMF, TDLC, PJUD, DIP) | agente (MCP open-legal-chile) |
| `dossier` | `dossier.md` — hechos con fuente; lo no verificado, aparte | agente + NVIDIA |
| `borrador` | `borrador.md` | agente |
| `pase` | `pase_*.md` — apertura, titulares y riesgo legal | Claude Opus |
| `qa` | `qa_resultado.md` — redundancia, LanguageTool, verificador | script |
| `cierre` | `cierre.md` — hecho, pendiente y **no verificado** | script |

## Cobertura: el corazón del trabajo

La información de un caso chileno está desparramada en diez medios, cada uno con un
pedazo. El trabajo es agruparla, ordenarla y verificar.

Barrido nacional primero: CIPER, LaBot, Interferencia, El Mostrador, Pauta, Ex-Ante,
The Clinic, El Desconcierto, Timeline, El Periodista; después Diario Financiero, La
Tercera, El Mercurio, BioBioChile y CNN Chile; y los regionales del caso —ahí suele
estar el dato que nadie más tiene—. Verificadores (Fast Check CL, Mala Espina) e
internacionales (ICIJ, OCCRP, Bellingcat, Reuters, AP, BBC Mundo, El País América,
La Nación, Folha) solo si el caso tiene arista exterior.

Reglas: cada medio con enlace, fecha y autor; no se copian párrafos, se resume el
aporte de cada uno; un dato que aparece en un solo medio es pista, no hecho; si dos
medios se contradicen se anota la contradicción y se busca el documento que la
resuelva. Lo que nadie publicó también es un hallazgo: el vacío se anota.

## Documentos ya emitidos antes que transparencia

La Ley 20.285 es el último camino, no el primero. Casi todo está publicado: informes
finales de Contraloría (9.600+), dictámenes, sanciones ambientales de la SMA,
resoluciones del SII, sanciones de la CMF, jurisprudencia del TDLC, sentencias del
PJUD, declaraciones de intereses y patrimonio de InfoProbidad, expedientes del SEIA y
compras en Mercado Público.

Solo si el documento no existe se propone una solicitud de transparencia, y queda
anotada en el cierre como pendiente.

## Reparto de motores

| Etapa | Motor | Costo |
|---|---|---|
| Cobertura, lectura de expedientes, extracción, clasificación, embeddings | NVIDIA NIM (trial) | $0 |
| Apertura, titulares, riesgo legal, pase final | Claude (Opus / Sonnet) | plan Pro |
| Respaldo cuando se agota la cuota de Claude | Antigravity (Gemini 4 Argon / 3.8 Flash) | plan AI Pro |

## Reglas que el sistema no puede romper

- **Nunca publica.** No sube a Substack, no envía nada, no marca nada como publicado.
- **Cada hecho lleva fuente.** Lo no verificado se declara en su propia sección.
- **Los límites de `no_tocar` se respetan** sin excepción, incluso si el ángulo queda
  más débil por eso.
- **Un hueco declarado es periodismo; un hueco tapado es un error publicado.**

## Operación manual

```bash
P=kit-journalism/.venv/bin/python
S=kit-journalism/scripts/pipeline_editorial.py

$P $S abrir   --tema "..." --tipo nota     # crear agenda + expediente
$P $S estado                               # ver qué etapa falta
$P $S marcar  --etapa cobertura
$P $S pase    --tarea pase_completo --motor claude
$P $S pase    --motor agy                  # respaldo con Gemini
$P $S qa                                   # controles automáticos
$P $S cerrar                               # resumen final
```

Para reactivar el radar matinal, si algún día se quiere:

```bash
hermes cron resume bf4c6c24196c
```
