#!/usr/bin/env python3
"""
generar_grafo_vinculos.py - Última Prensa Journalism Kit
Construye grafos interactivos de conocimiento y redes de vínculos
para investigaciones periodísticas (personas, empresas, inmuebles, decretos, fondos).
Exporta en:
  1. Mermaid Diagram (para Markdown / Substack)
  2. HTML Interactivo con PyVis / Vis.js (para reportajes multimedia y visualización web)
"""

import sys
import json
import argparse
from pathlib import Path
import networkx as nx
from pyvis.network import Network

# Esquema de colores periodísticos por categoría
COLOR_MAP = {
    "autoridad": {"color": "#1E3A8A", "shape": "dot", "size": 28},        # Azul marino (Rector, Vicerrector)
    "sociedad": {"color": "#3B82F6", "shape": "box", "size": 24},         # Azul medio (ULA, CASUL, IP)
    "privado": {"color": "#D97706", "shape": "dot", "size": 26},          # Ámbar/Naranja (Huincahue, Sutil)
    "politica": {"color": "#9333EA", "shape": "diamond", "size": 25},      # Púrpura (PDG, Cerda)
    "inmueble": {"color": "#10B981", "shape": "hexagon", "size": 26},      # Esmeralda (Cochrane, Lynch)
    "judicial": {"color": "#DC2626", "shape": "triangle", "size": 30},     # Rojo (Juez, Sentencia, Quiebra)
    "recurso": {"color": "#F59E0B", "shape": "star", "size": 22},          # Dorado ($1.200M GORE, Deudas)
    "asesor": {"color": "#6B7280", "shape": "ellipse", "size": 20}         # Gris (Ferrada, Ríos Labbé)
}

def export_mermaid(graph: nx.DiGraph, title: str = "Red de Vínculos del Caso") -> str:
    """Genera código Mermaid para incrustar en Markdown."""
    lines = ["```mermaid", f"---", f"title: {title}", f"---", "graph TD"]
    
    # Declarar nodos con estilos
    for node, data in graph.nodes(data=True):
        label = data.get("label", node)
        cat = data.get("cat", "sociedad")
        # Sanitizar label para Mermaid
        safe_label = label.replace('"', "'")
        lines.append(f'    {node}["{safe_label}"]')
    
    # Declarar aristas
    for u, v, data in graph.edges(data=True):
        rel = data.get("rel", "")
        if rel:
            lines.append(f'    {u} -->|"{rel}"| {v}')
        else:
            lines.append(f'    {u} --> {v}')
            
    lines.append("```")
    return "\n".join(lines)

def export_pyvis_html(graph: nx.DiGraph, output_html: Path, title: str = "Grafo de Vínculos"):
    """Genera un archivo HTML interactivo con física, zoom y filtros."""
    net = Network(height="750px", width="100%", bgcolor="#0F172A", font_color="#F8FAFC", directed=True)
    
    for node, data in graph.nodes(data=True):
        cat = data.get("cat", "sociedad")
        style = COLOR_MAP.get(cat, {"color": "#64748B", "shape": "dot", "size": 20})
        net.add_node(
            node,
            label=data.get("label", node),
            title=f"<b>{data.get('label', node)}</b><br>Tipo: {cat.upper()}<br>{data.get('desc', '')}",
            color=style["color"],
            shape=style["shape"],
            size=style["size"]
        )
        
    for u, v, data in graph.edges(data=True):
        net.add_edge(
            u, v,
            title=data.get("rel", ""),
            label=data.get("rel", ""),
            color="#94A3B8",
            arrows="to"
        )
        
    net.set_options("""
    var options = {
      "nodes": {
        "font": {
          "size": 14,
          "face": "Inter, system-ui, sans-serif"
        }
      },
      "edges": {
        "color": {
          "inherit": true
        },
        "smooth": {
          "type": "continuous"
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -4000,
          "centralGravity": 0.3,
          "springLength": 120,
          "springConstant": 0.04
        },
        "minVelocity": 0.75
      }
    }
    """)
    
    net.write_html(str(output_html))
    print(f"[✓] Grafo interactivo exportado en: {output_html}")

def load_case_graph(json_file: Path) -> nx.DiGraph:
    """Carga los nodos y aristas desde un archivo JSON estructurado."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    G = nx.DiGraph()
    for n in data.get("nodos", []):
        G.add_node(n["id"], label=n.get("label", n["id"]), cat=n.get("cat", "sociedad"), desc=n.get("desc", ""))
        
    for e in data.get("vinculos", []):
        G.add_edge(e["origen"], e["destino"], rel=e.get("relacion", ""))
        
    return G

def main():
    parser = argparse.ArgumentParser(description="Generador de Grafos de Conocimiento y Vínculos para Última Prensa")
    parser.add_argument("--data", type=str, required=True, help="Archivo JSON con los datos del grafo")
    parser.add_argument("--out-html", type=str, default="notas_y_datos/grafo_interactivo.html", help="Ruta de salida del HTML interactivo")
    parser.add_argument("--out-md", type=str, default="notas_y_datos/grafo_mermaid.md", help="Ruta de salida para Mermaid Markdown")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"[X] Archivo de datos no encontrado: {data_path}")
        sys.exit(1)

    graph = load_case_graph(data_path)
    print(f"[*] Grafo cargado con {graph.number_of_nodes()} nodos y {graph.number_of_edges()} relaciones.")

    # 1. Exportar HTML Interactivo
    out_html = Path(args.out_html)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    export_pyvis_html(graph, out_html, title=data_path.stem)

    # 2. Exportar Mermaid Markdown
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    mermaid_code = export_mermaid(graph, title=f"Red de Vínculos: {data_path.stem}")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(mermaid_code)
    print(f"[✓] Diagrama Mermaid exportado en: {out_md}")

if __name__ == "__main__":
    main()
