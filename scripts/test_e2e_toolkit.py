#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Última Prensa - Suite de Pruebas End-to-End (E2E) del Toolkit
====================================================================
"""

import sys
import os
import json
import shutil
import tempfile
import subprocess
from pathlib import Path

PYTHON_BIN = sys.executable
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

def run_step(step_name: str, func) -> bool:
    print(f"\n{'='*70}")
    print(f"[*] INICIANDO TEST: {step_name}")
    print(f"{'='*70}")
    try:
        func()
        print(f"[✓] {step_name}: APROBADO EXITOSAMENTE")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[X] {step_name}: FALLÓ (CalledProcessError)")
        print(f"    STDOUT:\n{e.stdout}")
        print(f"    STDERR:\n{e.stderr}")
        return False
    except Exception as e:
        print(f"[X] {step_name}: FALLÓ -> {e}")
        import traceback
        traceback.print_exc()
        return False

def test_calculo_ratios():
    script = SCRIPTS_DIR / "calculo_ratios_municipales.py"
    cmd = [
        PYTHON_BIN, str(script),
        "--comuna", "Osorno",
        "--poblacion", "173000",
        "--caja", "4500000000",
        "--pasivos", "3200000000",
        "--honorarios", "850000000",
        "--gastos-personal", "3200000000"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "ÍNDICE DE LIQUIDEZ CORRIENTE" in res.stdout, "Falta Liquidez Corriente"
    assert "PESO DEL PERSONAL A HONORARIOS" in res.stdout, "Falta Ratio de Honorarios"
    print("   Salida de ratios financieros verificada correctamente.")

def test_grafo_vinculos(tmp_dir: Path):
    script = SCRIPTS_DIR / "generar_grafo_vinculos.py"
    test_json = tmp_dir / "caso_test_grafo.json"
    data = {
        "nodos": [
            {"id": "alcalde", "label": "Jaime Bertin", "cat": "autoridad", "desc": "Alcalde de Osorno"},
            {"id": "constructora", "label": "Constructora Sur SpA", "cat": "sociedad", "desc": "Contratista adjudicado"},
            {"id": "licitacion", "label": "Licitación Pileta Plaza", "cat": "recurso", "desc": "$504 millones de inversión"}
        ],
        "vinculos": [
            {"origen": "alcalde", "destino": "licitacion", "relacion": "Decreto de adjudicación"},
            {"origen": "constructora", "destino": "licitacion", "relacion": "Oferente adjudicado"}
        ]
    }
    test_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    out_html = tmp_dir / "grafo.html"
    out_md = tmp_dir / "grafo.md"
    out_ftm = tmp_dir / "grafo.ftm.jsonl"
    
    cmd = [
        PYTHON_BIN, str(script),
        "--data", str(test_json),
        "--out-html", str(out_html),
        "--out-md", str(out_md),
        "--out-ftm", str(out_ftm)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise subprocess.CalledProcessError(res.returncode, cmd, output=res.stdout, stderr=res.stderr)
    
    assert out_html.exists() and out_html.stat().st_size > 500, "HTML no generado"
    assert out_md.exists() and "```mermaid" in out_md.read_text(encoding="utf-8"), "Mermaid MD no generado"
    assert out_ftm.exists() and out_ftm.stat().st_size > 100, "FollowTheMoney JSONL no generado"
    
    lines = out_ftm.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 3, "Entidades FTM insuficientes"
    first_ent = json.loads(lines[0])
    assert "schema" in first_ent and "id" in first_ent, "Estructura FTM inválida"
    print("   Salidas HTML, Mermaid y FollowTheMoney JSONL validadas.")

def test_exportar_substack(tmp_dir: Path):
    script = SCRIPTS_DIR / "exportar_substack.py"
    in_md = tmp_dir / "reportaje_prueba.md"
    in_md.write_text("""# La trama secreta del financiamiento municipal en Los Lagos

Una auditoría forense a las cuentas de la casa consistorial revela anomalías por más de $500 millones.

Por Equipo de Investigación de Última Prensa

El examen a los registros contables demuestra que las adjudicaciones se realizaron sin el quórum requerido por la normativa de compras públicas.

## El origen del conflicto

La resolución judicial confirmó que los pagos a honorarios superaron el 25 % del presupuesto anual.

> «Las opiniones son libres, pero los hechos son sagrados.»
""", encoding="utf-8")

    out_html = tmp_dir / "reportaje_substack.html"
    cmd = [PYTHON_BIN, str(script), str(in_md), str(out_html)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise subprocess.CalledProcessError(res.returncode, cmd, output=res.stdout, stderr=res.stderr)
    
    assert out_html.exists(), "Archivo Substack HTML no generado"
    content = out_html.read_text(encoding="utf-8")
    assert "text-align: justify" in content or "textAlign" in content or "justify" in content, "Falta alineación justificada obligatoria"
    print("   HTML para Substack exportado y verificado con justificación tipográfica.")

def test_compilador_expediente_pdf(tmp_dir: Path):
    script = SCRIPTS_DIR / "compilador_expediente_pdf.py"
    in_md = tmp_dir / "denuncia_test.md"
    in_md.write_text("""# DENUNCIA ANTE CONTRALORÍA GENERAL DE LA REPÚBLICA

**DENUNCIANTE:** Equipo Pericial Última Prensa  
**ORGANISMO DENUNCIADO:** Ilustre Municipalidad de Osorno  

## I. RELACIÓN DE HECHOS

Se constata la omisión reiterada de antecedentes en compras directas de servicios.
""", encoding="utf-8")

    out_pdf = tmp_dir / "expediente_test.pdf"
    cmd = [
        PYTHON_BIN, str(script),
        "--md", str(in_md),
        "--salida", str(out_pdf)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise subprocess.CalledProcessError(res.returncode, cmd, output=res.stdout, stderr=res.stderr)
    assert out_pdf.exists() and out_pdf.stat().st_size > 1000, "PDF no generado correctamente"
    print(f"   Expediente PDF compilado exitosamente ({out_pdf.stat().st_size} bytes).")

def test_ingestar_documentos_md(tmp_dir: Path):
    script = SCRIPTS_DIR / "ingestar_documentos_md.py"
    docs_dir = tmp_dir / "documentos_in"
    docs_dir.mkdir(parents=True, exist_ok=True)
    out_dir = tmp_dir / "markdown_out"
    
    sample_txt = docs_dir / "oficio_contraloria.txt"
    sample_txt.write_text("REPÚBLICA DE CHILE\nCONTRALORÍA GENERAL\nDICTAMEN E123456\nSobre asignación de funciones.", encoding="utf-8")
    
    cmd = [
        PYTHON_BIN, str(script),
        "--dir", str(docs_dir),
        "--out", str(out_dir)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise subprocess.CalledProcessError(res.returncode, cmd, output=res.stdout, stderr=res.stderr)
    
    assert out_dir.exists(), "Directorio de salida no creado"
    out_md = out_dir / "oficio_contraloria.md"
    assert out_md.exists() and "DICTAMEN E123456" in out_md.read_text(encoding="utf-8"), "Contenido no ingerido"
    print("   Ingesta documental verificada correctamente.")

def test_investigacion_chile_mcp():
    script = SCRIPTS_DIR / "investigacion_chile_mcp.py"
    
    # 1. Initialize
    init_cmd = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    p1 = subprocess.run([PYTHON_BIN, str(script)], input=json.dumps(init_cmd), capture_output=True, text=True, check=True)
    res1 = json.loads(p1.stdout)
    assert res1.get("result", {}).get("serverInfo", {}).get("name") == "ultimaprensa-investigacion-chile", "Nombre de servidor incorrecto"
    
    # 2. Tools list
    list_cmd = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    p2 = subprocess.run([PYTHON_BIN, str(script)], input=json.dumps(list_cmd), capture_output=True, text=True, check=True)
    res2 = json.loads(p2.stdout)
    tool_names = [t["name"] for t in res2.get("result", {}).get("tools", [])]
    assert "infoprobidad_declaracion" in tool_names, "Falta infoprobidad_declaracion"
    assert "mercadopublico_buscar_licitaciones" in tool_names, "Falta mercadopublico_buscar_licitaciones"
    assert "ftm_crear_entidad" in tool_names, "Falta ftm_crear_entidad"
    
    # 3. Call tool FTM
    call_cmd = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "ftm_crear_entidad",
            "arguments": {
                "schema": "Person",
                "id": "cl-rut-12345678-9",
                "properties": {"name": ["Autoridad de Prueba"]}
            }
        }
    }
    p3 = subprocess.run([PYTHON_BIN, str(script)], input=json.dumps(call_cmd), capture_output=True, text=True, check=True)
    res3 = json.loads(p3.stdout)
    assert not res3.get("result", {}).get("isError", True), "Tool call FTM falló"
    print("   Servidor MCP de investigación chilena probado con éxito (initialize, tools/list, tools/call).")

def test_rae_mcp():
    script = SCRIPTS_DIR / "rae_mcp_server.py"
    init_cmd = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    p1 = subprocess.run([PYTHON_BIN, str(script)], input=json.dumps(init_cmd), capture_output=True, text=True, check=True)
    res1 = json.loads(p1.stdout)
    assert "protocolVersion" in res1.get("result", {}), "RAE MCP initialize falló"
    print("   Servidor MCP RAE validado con éxito.")

def main():
    tmp_dir = Path(tempfile.mkdtemp(prefix="up_e2e_test_"))
    print(f"[*] Directorio temporal de pruebas: {tmp_dir}")
    
    tests = [
        ("Cálculo de Ratios Municipales", test_calculo_ratios),
        ("Generador de Grafos y FollowTheMoney", lambda: test_grafo_vinculos(tmp_dir)),
        ("Exportador Tipográfico Substack", lambda: test_exportar_substack(tmp_dir)),
        ("Compilador de Expediente Pericial PDF", lambda: test_compilador_expediente_pdf(tmp_dir)),
        ("Ingesta Documental MarkItDown", lambda: test_ingestar_documentos_md(tmp_dir)),
        ("Servidor MCP de Investigación Chilena", test_investigacion_chile_mcp),
        ("Servidor MCP de la RAE", test_rae_mcp),
    ]
    
    passed = 0
    failed = 0
    
    for name, func in tests:
        ok = run_step(name, func)
        if ok:
            passed += 1
        else:
            failed += 1
            
    try:
        shutil.rmtree(tmp_dir)
    except Exception:
        pass
        
    print(f"\n{'='*70}")
    print(f"RESULTADOS E2E: {passed} Aprobados, {failed} Fallidos")
    print(f"{'='*70}")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
