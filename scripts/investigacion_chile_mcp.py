#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Última Prensa - Servidor MCP de Datos Públicos e Investigación
====================================================================
Servidor Model Context Protocol (MCP) para Antigravity IDE, Claude Code
y agentes de periodismo pericial de Última Prensa.

Herramientas incluidas:
1. infoprobidad_declaracion: Consulta y extracción pericial de declaraciones
   de intereses y patrimonio (DIP) de autoridades públicas.
2. mercadopublico_buscar_licitaciones: Búsqueda de licitaciones públicas en ChileCompra.
3. mercadopublico_orden_compra: Consulta detallada de órdenes de compra en Mercado Público.
4. mercadopublico_proveedor: Consulta de proveedores del Estado por RUT.
5. cgr_buscar_dictamen: Búsqueda y enlace a dictámenes de la Contraloría General.
6. ftm_crear_entidad: Estructuración canónica de entidades bajo el estándar FollowTheMoney (OCCRP).
"""

import sys
import json
import os
import re
import urllib.parse
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    if hasattr(sys.stdout, "reconfigure"):
        getattr(sys.stdout, "reconfigure")(encoding='utf-8')
    if hasattr(sys.stdin, "reconfigure"):
        getattr(sys.stdin, "reconfigure")(encoding='utf-8')
except Exception:
    pass

import requests

# Importar extractor_infoprobidad si está disponible
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import extractor_infoprobidad as ip_extractor
except ImportError:
    ip_extractor = None

# Constante de ticket de prueba público o de entorno para ChileCompra
MERCADOPUBLICO_TICKET = os.environ.get(
    "MERCADOPUBLICO_TICKET",
    "F853740D-122B-426B-9169-B0F6C0783F41"  # Ticket público de pruebas API v1
)

TOOLS = [
    {
        "name": "infoprobidad_declaracion",
        "description": "Descarga, parsea y estructura al 100 % una Declaración Jurada de Intereses y Patrimonio (DIP) de una autoridad pública desde InfoProbidad.cl. Retorna datos personales, bienes inmuebles, vehículos, sociedades, contratos y pasivos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "identificador": {
                    "type": "string",
                    "description": "URL completa de InfoProbidad (ej: 'https://www.infoprobidad.cl/Declaracion/Declaracion?ID=1698949'), ID numérico ('1698949') o hash de 32 caracteres."
                }
            },
            "required": ["identificador"]
        }
    },
    {
        "name": "mercadopublico_buscar_licitaciones",
        "description": "Consulta licitaciones públicas vigentes o históricas en Mercado Público (ChileCompra) según fecha, organismo público o término de búsqueda.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fecha": {
                    "type": "string",
                    "description": "Fecha en formato ddmmaaaa (ej: '23092026'). Por defecto es la fecha actual."
                },
                "codigo_organismo": {
                    "type": "string",
                    "description": "Código del organismo comprador (ej: '6948' para Municipalidad de Osorno). Opcional."
                },
                "palabra_clave": {
                    "type": "string",
                    "description": "Palabra clave para filtrar por nombre o descripción de la licitación (ej: 'seguridad', 'camiones', 'auditoría')."
                },
                "estado": {
                    "type": "string",
                    "description": "Filtrar por estado: 'publicada', 'cerrada', 'adjudicada', 'desierta', 'todos'. Por defecto 'publicada'."
                }
            }
        }
    },
    {
        "name": "mercadopublico_orden_compra",
        "description": "Consulta el detalle oficial de una orden de compra en Mercado Público / ChileCompra a partir de su código único o por fecha y organismo.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigo": {
                    "type": "string",
                    "description": "Código identificador de la orden de compra (ej: '6948-123-SE24')."
                },
                "fecha": {
                    "type": "string",
                    "description": "Fecha en formato ddmmaaaa si se consultan todas las órdenes de un día."
                },
                "codigo_organismo": {
                    "type": "string",
                    "description": "Código del organismo comprador para filtrar."
                }
            }
        }
    },
    {
        "name": "mercadopublico_proveedor",
        "description": "Consulta los antecedentes de un proveedor o contratista del Estado en ChileCompra a partir de su RUT o razón social.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rut": {
                    "type": "string",
                    "description": "RUT de la empresa o proveedor (con o sin puntos, con guion, ej: '76.123.456-7' o '76123456-7')."
                }
            },
            "required": ["rut"]
        }
    },
    {
        "name": "cgr_buscar_dictamen",
        "description": "Construye la búsqueda y consulta de jurisprudencia y dictámenes de la Contraloría General de la República (CGR) sobre materias administrativas y municipales.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "materia": {
                    "type": "string",
                    "description": "Materia jurídica o hecho investigado (ej: 'honorarios municipales', 'adjudicación licitación vicios', 'abandono de deberes')."
                },
                "numero_dictamen": {
                    "type": "string",
                    "description": "Número o código específico del dictamen si se conoce (ej: 'E450123/2024' o '012345N22')."
                }
            },
            "required": ["materia"]
        }
    },
    {
        "name": "ftm_crear_entidad",
        "description": "Crea una entidad canónica en formato FollowTheMoney (FTM) de OCCRP (Person, Company, PublicBody, Contract) lista para incorporarse al grafo de relaciones periciales.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "schema": {
                    "type": "string",
                    "enum": ["Person", "Company", "PublicBody", "Contract", "Ownership", "Payment"],
                    "description": "Esquema canónico de FollowTheMoney a utilizar."
                },
                "id": {
                    "type": "string",
                    "description": "Identificador único de la entidad (ej: 'cl-rut-76123456-7' o 'alcalde-osorno')."
                },
                "properties": {
                    "type": "object",
                    "description": "Propiedades de la entidad (ej: {'name': ['Juan Pérez'], 'idNumber': ['12.345.678-9'], 'country': ['cl']})."
                }
            },
            "required": ["schema", "id", "properties"]
        }
    }
]


def tool_infoprobidad_declaracion(identificador: str) -> Dict[str, Any]:
    if not ip_extractor:
        return {"error": "El módulo extractor_infoprobidad no está disponible."}
    
    try:
        html, id_detectado = ip_extractor.descargar_declaracion_html(identificador)
        if not html or len(html) < 200:
            return {"error": f"No se pudo descargar la declaración para el identificador: {identificador}"}
        
        datos = ip_extractor.parsear_declaracion(html)
        return {
            "status": "success",
            "id_declaracion": id_detectado,
            "declarante": datos.get("nombre_declarante"),
            "datos_personales": datos.get("datos_personales"),
            "datos_declaracion": datos.get("datos_declaracion"),
            "bienes_inmuebles": datos.get("bienes_inmuebles"),
            "vehiculos": datos.get("vehiculos"),
            "sociedades_empresas": datos.get("sociedades_empresas"),
            "pasivos_deudas": datos.get("pasivos_deudas"),
            "parientes": datos.get("parientes")
        }
    except Exception as e:
        return {"error": f"Fallo al procesar InfoProbidad: {str(e)}"}


def tool_mercadopublico_licitaciones(fecha: Optional[str] = None, codigo_organismo: Optional[str] = None, palabra_clave: Optional[str] = None, estado: Optional[str] = "publicada") -> Dict[str, Any]:
    fecha_consulta = fecha or datetime.now().strftime("%d%m%Y")
    ticket = MERCADOPUBLICO_TICKET
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha={fecha_consulta}&ticket={ticket}"
    if estado and estado != "todos":
        url += f"&estado={estado}"
    if codigo_organismo:
        url += f"&CodigoOrganismo={codigo_organismo}"
        
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            return {
                "status": "error",
                "codigo_http": resp.status_code,
                "mensaje": "La API de Mercado Público no respondió exitosamente o el ticket requiere renovación.",
                "url_consultada": url.replace(ticket, "TICKET_OCULTO")
            }
        
        data = resp.json()
        cantidad = data.get("Cantidad", 0)
        licitaciones = data.get("Listado", [])
        
        if palabra_clave and licitaciones:
            palabra = palabra_clave.lower()
            licitaciones = [
                lic for lic in licitaciones
                if palabra in lic.get("Nombre", "").lower() or palabra in lic.get("Descripcion", "").lower()
            ]
            cantidad = len(licitaciones)
            
        return {
            "status": "success",
            "fecha": fecha_consulta,
            "cantidad_total": cantidad,
            "licitaciones": licitaciones[:30]  # Limitar a las primeras 30 para optimizar contexto
        }
    except Exception as e:
        return {"status": "error", "error": f"Excepción al conectar con Mercado Público: {str(e)}"}


def tool_mercadopublico_orden_compra(codigo: Optional[str] = None, fecha: Optional[str] = None, codigo_organismo: Optional[str] = None) -> Dict[str, Any]:
    ticket = MERCADOPUBLICO_TICKET
    if codigo:
        url = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?codigo={codigo}&ticket={ticket}"
    else:
        fecha_consulta = fecha or datetime.now().strftime("%d%m%Y")
        url = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha={fecha_consulta}&ticket={ticket}"
        if codigo_organismo:
            url += f"&CodigoOrganismo={codigo_organismo}"

    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            return {
                "status": "error",
                "codigo_http": resp.status_code,
                "mensaje": "Error de respuesta desde el servicio de órdenes de compra."
            }
        return {"status": "success", "data": resp.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def tool_mercadopublico_proveedor(rut: str) -> Dict[str, Any]:
    # Limpiar RUT
    rut_limpio = rut.replace(".", "").replace("-", "").strip()
    ticket = MERCADOPUBLICO_TICKET
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/empresas/buscarproveedor.json?rutempresaproveedor={rut_limpio}&ticket={ticket}"
    
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            return {"status": "success", "rut": rut, "data": data}
        else:
            return {
                "status": "partial",
                "rut": rut,
                "portal_url": f"https://www.mercadopublico.cl/Portal/Modules/Site/Busqueda/BusquedaProveedor.aspx?qs={rut_limpio}",
                "mensaje": "No se pudo consultar directamente la API JSON; se provee la URL de consulta directa del portal."
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def tool_cgr_buscar_dictamen(materia: str, numero_dictamen: Optional[str] = None) -> Dict[str, Any]:
    params = {"q": materia}
    if numero_dictamen:
        params["num"] = numero_dictamen
    query_str = urllib.parse.urlencode(params)
    url_portal = f"https://www.contraloria.cl/jurisprudencia/busqueda?{query_str}"
    
    return {
        "status": "success",
        "materia": materia,
        "numero_dictamen": numero_dictamen,
        "portal_cgr_url": url_portal,
        "instrucciones": "Para acceder al texto íntegro y dictámenes relacionados, consultar la URL provista con la herramienta fetch de MCP."
    }


def tool_ftm_crear_entidad(schema: str, id: str, properties: Dict[str, List[Any]]) -> Dict[str, Any]:
    try:
        from followthemoney import model
        entity = model.make_entity(schema)
        entity.id = id
        for prop, values in properties.items():
            if not isinstance(values, list):
                values = [values]
            for val in values:
                entity.add(prop, val)
        return {
            "status": "success",
            "followthemoney_entity": entity.to_dict()
        }
    except Exception as e:
        # Fallback si no está cargado el modelo FTM
        return {
            "status": "success_fallback",
            "schema": schema,
            "id": id,
            "properties": properties,
            "note": f"Estructurado canónicamente. ({e})"
        }


def handle_tool_call(name: str, args: Dict[str, Any]) -> Any:
    if name == "infoprobidad_declaracion":
        return tool_infoprobidad_declaracion(args.get("identificador", ""))
    elif name == "mercadopublico_buscar_licitaciones":
        return tool_mercadopublico_licitaciones(
            fecha=args.get("fecha"),
            codigo_organismo=args.get("codigo_organismo"),
            palabra_clave=args.get("palabra_clave"),
            estado=args.get("estado", "publicada")
        )
    elif name == "mercadopublico_orden_compra":
        return tool_mercadopublico_orden_compra(
            codigo=args.get("codigo"),
            fecha=args.get("fecha"),
            codigo_organismo=args.get("codigo_organismo")
        )
    elif name == "mercadopublico_proveedor":
        return tool_mercadopublico_proveedor(args.get("rut", ""))
    elif name == "cgr_buscar_dictamen":
        return tool_cgr_buscar_dictamen(
            materia=args.get("materia", ""),
            numero_dictamen=args.get("numero_dictamen")
        )
    elif name == "ftm_crear_entidad":
        return tool_ftm_crear_entidad(
            schema=args.get("schema", ""),
            id=args.get("id", ""),
            properties=args.get("properties", {})
        )
    else:
        return {"error": f"Herramienta desconocida: {name}"}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "ultimaprensa-investigacion-chile",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOLS}
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
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
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
