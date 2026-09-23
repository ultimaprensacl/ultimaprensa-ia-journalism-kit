#!/usr/bin/env bash
# ====================================================================
# Última Prensa IA Journalism Kit - Instalador Automático de 1 Comando
# ====================================================================
# Configura el entorno virtual, instala dependencias periciales,
# enlaza los servidores MCP para Antigravity Desktop/IDE y corre el test E2E.
#
# Uso:
#   chmod +x install.sh
#   ./install.sh
# ====================================================================

set -e

echo "===================================================================="
echo "  Iniciando instalación de Última Prensa IA Journalism Kit"
echo "===================================================================="

# 1. Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "[X] Error: Python 3 no está instalado en el sistema."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[*] Python detectado: versión $PY_VERSION"

# 2. Crear entorno virtual si no existe
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "[*] Creando entorno virtual en .venv..."
    python3 -m venv .venv
else
    echo "[✓] Entorno virtual existente detectado en .venv."
fi

VENV_PY="$SCRIPT_DIR/.venv/bin/python"
VENV_PIP="$SCRIPT_DIR/.venv/bin/pip"

# 3. Instalar o actualizar dependencias
echo "[*] Instalando dependencias desde requirements.txt..."
"$VENV_PIP" install --quiet --upgrade pip
"$VENV_PIP" install --quiet -r requirements.txt

# 4. Configurar .env si no existe
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "[*] Creando archivo local .env desde .env.example..."
    cp .env.example .env
fi

# 5. Configurar o actualizar .vscode/mcp.json con rutas absolutas locales
mkdir -p .vscode
echo "[*] Configurando servidores MCP para Antigravity Desktop / IDE..."
cat <<EOF > .vscode/mcp.json
{
  "mcpServers": {
    "investigacion-chile": {
      "command": "$VENV_PY",
      "args": [
        "$SCRIPT_DIR/scripts/investigacion_chile_mcp.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "$SCRIPT_DIR/scripts"
      }
    },
    "fetch": {
      "command": "$SCRIPT_DIR/.venv/bin/mcp-server-fetch",
      "args": ["--ignore-robots-txt"]
    },
    "git": {
      "command": "$SCRIPT_DIR/.venv/bin/mcp-server-git",
      "args": [
        "--repository",
        "$SCRIPT_DIR"
      ]
    },
    "rae-api": {
      "command": "$VENV_PY",
      "args": [
        "$SCRIPT_DIR/scripts/rae_mcp_server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "$SCRIPT_DIR/scripts"
      }
    }
  }
}
EOF

# 6. Ejecutar suite de pruebas End-to-End para certificar instalación
echo "[*] Ejecutando suite de pruebas End-to-End de certificación..."
"$VENV_PY" scripts/test_e2e_toolkit.py

echo ""
echo "===================================================================="
echo "  ✓ INSTALACIÓN COMPLETADA EXITOSAMENTE"
echo "===================================================================="
echo "  Para comenzar a trabajar en Antigravity Desktop o Antigravity IDE:"
echo ""
echo "  1. Abre Antigravity Desktop / IDE."
echo "  2. Selecciona 'Open Folder' (Abrir Carpeta) y elige esta ruta:"
echo "     $SCRIPT_DIR"
echo "  3. Abre el panel de chat con el agente e inicia tu investigación o"
echo "     columna de opinión. El agente detectará automáticamente las"
echo "     skills, reglas y servidores MCP periciales de Chile."
echo "===================================================================="
