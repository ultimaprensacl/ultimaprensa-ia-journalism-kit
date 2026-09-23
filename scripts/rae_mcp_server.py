#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor MCP (Model Context Protocol) para la API de la Real Academia Española (RAE).
Servicio: https://rae-api.com (https://github.com/rae-api-com)
Permite a Antigravity, Claude Code, Cursor y otros agentes consultar el Diccionario
de la Lengua Española (DLE) y auditar normas de puntuación y ortografía de la RAE.
"""

import sys
import json
import os

try:
    if hasattr(sys.stdout, "reconfigure"):
        getattr(sys.stdout, "reconfigure")(encoding='utf-8')
    if hasattr(sys.stdin, "reconfigure"):
        getattr(sys.stdin, "reconfigure")(encoding='utf-8')
except Exception:
    pass

from rae_client import RaeClient

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.environ.get("RAE_API_KEY", "")
client = RaeClient(api_key=API_KEY)

TOOLS = [
    {
        "name": "rae_get_word",
        "description": "Consulta una palabra en el Diccionario de la Lengua Española (DLE / RAE). Retorna definiciones, acepciones, etimología, categoría gramatical, sinónimos y antónimos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "Palabra a buscar en el diccionario (ej: 'concesión', 'simulación', 'canon', 'vía')."
                }
            },
            "required": ["word"]
        }
    },
    {
        "name": "rae_search",
        "description": "Busca lemas, palabras o expresiones en el catálogo de la RAE.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Término o consulta de búsqueda."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "rae_daily_word",
        "description": "Obtiene la palabra del día según la Real Academia Española (RAE).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "rae_random_word",
        "description": "Obtiene una palabra aleatoria del diccionario de la RAE con su definición.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "rae_validate_text",
        "description": "Audita un texto o archivo para verificar el estricto cumplimiento de las normas de puntuación y ortografía de la RAE (Ortografía 2010), detectando vicios del modelo anglosajón (puntuación dentro de comillas, falta de signos de apertura ¿ ¡, comillas inglesas como principales, porcentajes sin espacio y espaciado de rayas de inciso).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Texto en español a validar."
                }
            },
            "required": ["text"]
        }
    }
]


def handle_tool_call(name: str, arguments: dict) -> dict:
    try:
        if name == "rae_get_word":
            word = arguments.get("word", "")
            if not word:
                return {"error": "Se requiere el argumento 'word'"}
            return client.get_word(word)

        elif name == "rae_search":
            query = arguments.get("query", "")
            if not query:
                return {"error": "Se requiere el argumento 'query'"}
            return client.search(query)

        elif name == "rae_daily_word":
            return client.get_daily_word()

        elif name == "rae_random_word":
            return client.get_random_word()

        elif name == "rae_validate_text":
            text = arguments.get("text", "")
            if not text:
                return {"error": "Se requiere el argumento 'text'"}
            errs = client.validar_normas_rae(text)
            return {
                "ok": True,
                "errores_detectados": len(errs),
                "detalles": errs if errs else "Texto conforme a las normas ortotipográficas de la RAE."
            }

        else:
            return {"error": f"Herramienta desconocida: {name}"}

    except Exception as e:
        return {"error": f"Error al ejecutar {name}: {str(e)}"}


def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if not line:
                continue

            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if req_id is None:
                # Las notificaciones (como notifications/initialized) no deben recibir respuesta
                continue

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "rae-api-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                res = handle_tool_call(tool_name, tool_args)
                is_error = isinstance(res, dict) and "error" in res
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(res, ensure_ascii=False, indent=2)
                            }
                        ],
                        "isError": is_error
                    }
                }
            elif method == "ping":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {}
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Método no encontrado: {method}"
                    }
                }

            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
