#!/usr/bin/env bash
# =====================================================================
# configurar_nvidia_key.sh — Guarda la clave de NVIDIA NIM sin que quede
# en el historial del shell ni en el chat.
#
# Uso:
#     bash kit-journalism/scripts/configurar_nvidia_key.sh
#     bash kit-journalism/scripts/configurar_nvidia_key.sh --archivo ~/clave.txt
#
# Pide la clave con la entrada oculta, la deja en kit-journalism/.env y en
# ~/.hermes/.env (permisos 600) y verifica de inmediato contra la API.
#
#   --archivo <ruta>   lee la clave de un archivo local (creado con cualquier
#                      editor) y lo borra sobrescribiéndolo después de guardarla
#   --conservar        no borra el archivo de origen
#
# Obtén la clave gratis en https://build.nvidia.com/settings/api-keys
# =====================================================================
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROYECTO="$(dirname "$AQUI")"
ENV_PROYECTO="${NVIDIA_ENV_PROYECTO:-$PROYECTO/.env}"
ENV_HERMES="${NVIDIA_ENV_HERMES:-$HOME/.hermes/.env}"

archivo=""
conservar=0
while [ $# -gt 0 ]; do
  case "$1" in
    --archivo)   archivo="${2:-}"; shift 2 ;;
    --conservar) conservar=1; shift ;;
    -h|--help)   sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)           echo "Opción desconocida: $1" >&2; exit 2 ;;
  esac
done

leer_clave() {
  if [[ -t 0 ]]; then
    read -rsp "Clave de NVIDIA (nvapi-...): " clave
    echo
  else
    # Entrada por tubería (para uso desatendido sin exponerla en ps).
    IFS= read -r clave
  fi
}

guardar() {
  local archivo="$1"
  [[ -e "$archivo" ]] || { mkdir -p "$(dirname "$archivo")"; : > "$archivo"; chmod 600 "$archivo"; }
  local temporal
  temporal="$(mktemp)"
  grep -v '^NVIDIA_API_KEY=' "$archivo" > "$temporal" || true
  printf 'NVIDIA_API_KEY=%s\n' "$clave" >> "$temporal"
  cat "$temporal" > "$archivo"          # conserva dueño y permisos del original
  rm -f "$temporal"
  chmod 600 "$archivo"                  # el .env no queda legible por terceros
  echo "  guardada en $archivo (permisos 600)"
}

if [ -n "$archivo" ]; then
  [ -r "$archivo" ] || { echo "No puedo leer el archivo: $archivo" >&2; exit 1; }
  clave="$(tr -d '[:space:]' < "$archivo")"
  echo "  clave leída de $archivo"
else
  leer_clave
fi
clave="${clave//[$'\r\n']/}"

if [[ -z "$clave" ]]; then
  echo "No se ingresó ninguna clave." >&2
  exit 1
fi
if [[ "$clave" != nvapi-* ]]; then
  echo "Aviso: la clave no empieza con 'nvapi-'. Se guarda igual, pero revisa que sea la correcta." >&2
fi

guardar "$ENV_PROYECTO"
guardar "$ENV_HERMES"

# El archivo de origen, si lo hubo, se sobrescribe antes de borrarse: la clave
# ya vive en los .env con permisos 600 y no tiene por qué quedar en el escritorio.
if [ -n "$archivo" ] && [ "$conservar" = "0" ]; then
  origen="$(readlink -f "$archivo" 2>/dev/null || printf '%s' "$archivo")"
  if [ "$origen" != "$(readlink -f "$ENV_PROYECTO" 2>/dev/null || printf '%s' "$ENV_PROYECTO")" ] \
     && [ "$origen" != "$(readlink -f "$ENV_HERMES" 2>/dev/null || printf '%s' "$ENV_HERMES")" ]; then
    python3 - "$origen" <<'PY'
import os, sys
ruta = sys.argv[1]
tamano = os.path.getsize(ruta)
with open(ruta, "r+b") as f:
    f.write(b"\0" * tamano)
    f.flush()
    os.fsync(f.fileno())
os.unlink(ruta)
PY
    echo "  archivo de origen sobrescrito y borrado"
  fi
fi

echo
echo "Verificando contra la API…"
# El catálogo (GET /v1/models) responde sin autenticación, así que la única
# comprobación real es una inferencia mínima.
respuesta="$(curl -s -o /dev/null -w '%{http_code}' \
  -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $clave" \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/nemotron-3-ultra-550b-a55b","messages":[{"role":"user","content":"Responde solo: ok"}],"max_tokens":200}' \
  || true)"

case "$respuesta" in
  200) echo "  Clave válida y con inferencia funcionando."
       echo "     python kit-journalism/scripts/nvidia_router.py estado" ;;
  401) echo "  La API no recibió una clave válida (HTTP 401)." >&2 ;;
  403) echo "  La API rechazó la clave (HTTP 403: Authorization failed)." >&2
       echo "  Genera una nueva en https://build.nvidia.com/settings/api-keys" >&2 ;;
  404) echo "  Clave válida, pero este modelo no está habilitado para tu cuenta (HTTP 404)." >&2
       echo "  El catálogo lista modelos que la cuenta no puede usar." >&2
       echo "  Sondea los tuyos: python kit-journalism/scripts/nvidia_router.py estado" >&2 ;;
  429) echo "  Clave aceptada. Límite de peticiones alcanzado en este momento (HTTP 429)." ;;
  *) echo "  No se pudo confirmar (HTTP $respuesta). La clave quedó guardada; revisa la red." >&2 ;;
esac
