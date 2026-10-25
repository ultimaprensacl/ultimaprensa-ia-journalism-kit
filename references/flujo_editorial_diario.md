# Flujo editorial diario

Una pieza al día, de lunes a viernes: **reportaje grande lunes y miércoles**,
**nota el resto**. El sistema trabaja de noche y a las 07:00 el borrador está en
disco con su control de calidad pasado. La firma y la publicación son del editor.

## Las piezas

| Pieza | Dónde vive | Quién la provee |
|---|---|---|
| Agenda del día | `reportajes/_agenda/AAAA-MM-DD.md` | El editor. Sin agenda no hay investigación. |
| Andamiaje y control | `kit-journalism/scripts/pipeline_editorial.py` | Script: abre, marca etapas, lanza el pase, corre QA, cierra |
| Procedimiento | skill `ultimaprensa-diario` | Hermes, cargada por el cron |
| Disparador | cron `bf4c6c24196c`, días hábiles 07:00 | Hermes |

## Rutina del editor

La noche anterior, o a primera hora:

```bash
cd ~/Escritorio/Ultimaprensa
kit-journalism/.venv/bin/python kit-journalism/scripts/pipeline_editorial.py agenda
```

Crea `reportajes/_agenda/<hoy>.md` con el tipo ya puesto según el día (lunes y
miércoles, reportaje). Se completa a mano: `tema`, `angulo`, `apuntar_a`,
`fuentes_clave`, `no_tocar` y `extension`.

Si a las 07:00 el archivo no existe o no tiene tema, el agente **no investiga**:
entrega cinco temas candidatos con su fuente primaria y dice cuál elegiría.

## Lo que hace el agente

1. **Abrir**: crea `reportajes/<fecha>_<slug>/` con `brief.md` y `estado.json`.
2. **Radar**: búsqueda web y fuentes primarias; escribe `radar.md`.
3. **Contexto jurídico**: herramientas MCP de open-legal-chile; escribe `legal.md`.
4. **Dossier**: NVIDIA extrae datos duros del expediente; cada hecho con su fuente.
5. **Borrador**: `borrador.md` con las reglas de `AGENTS.md`.
6. **Pase**: Claude Opus reescribe la apertura, propone titulares y lista las
   imputaciones sin prueba suficiente.
7. **QA**: redundancia léxica, LanguageTool y verificador del kit.
8. **Cierre**: `cierre.md` con lo hecho, lo pendiente y **lo que quedó sin verificar**.

## Reparto de motores

| Etapa | Motor | Costo |
|---|---|---|
| Radar, lectura de expedientes, extracción, clasificación, embeddings | NVIDIA NIM (trial) | $0 |
| Apertura, titulares, riesgo legal, pase final | Claude (Opus / Sonnet) | plan Pro |
| Respaldo cuando se agota la cuota de Claude | Antigravity (Gemini 4 Argon / 3.8 Flash) | plan AI Pro |

## Reglas que el sistema no puede romper

- **Nunca publica.** No sube a Substack, no envía nada, no marca nada como publicado.
- **Cada hecho lleva fuente.** Lo no verificado se declara en su propia sección.
- **Los límites de `no_tocar` se respetan** sin excepción, incluso si el ángulo
  periodístico queda más débil por eso.
- **Un hueco declarado es periodismo; un hueco tapado es un error publicado.**

## Operación manual

```bash
P=kit-journalism/.venv/bin/python
S=kit-journalism/scripts/pipeline_editorial.py

$P $S agenda  --fecha 2026-10-27          # crear la agenda del día
$P $S abrir   --fecha 2026-10-27          # abrir el expediente
$P $S estado  --fecha 2026-10-27          # ver qué etapa falta
$P $S marcar  --fecha 2026-10-27 --etapa dossier
$P $S pase    --fecha 2026-10-27 --tarea pase_completo --motor claude
$P $S pase    --fecha 2026-10-27 --motor agy        # respaldo con Gemini
$P $S qa      --fecha 2026-10-27          # controles automáticos
$P $S cerrar  --fecha 2026-10-27          # resumen final
```

Para correr el ciclo completo ahora sin esperar al cron, se le pide al agente en el
chat, o se dispara el job con `cronjob_manage action='run' job_id='bf4c6c24196c'`.

## Cambiar el horario o los días

El cron es `weekdays at 7am`. Para moverlo:

```bash
hermes cron list
hermes cron update bf4c6c24196c --schedule "weekdays at 6am"
```

Si algún día el reportaje grande va martes y jueves en vez de lunes y miércoles,
se cambia en dos lugares: el tipo por defecto en `comando_agenda()`
(`weekday() in (0, 2)`) y, si cambia qué días hay pieza, la programación del cron.
