#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_animaciones_claras.py — Motor de Infografías y Animaciones Claras / Fondo Blanco Mate
Última Prensa IA Journalism Kit

Genera todos los cuadros del reportaje en fondo 100 % blanco mate / marfil elegante
con animaciones fluidas continuas (WebP y GIF) sin bordes oscuros ni fondos grises.
"""

import os
import sys
import subprocess
from pathlib import Path

CHROME_BIN = "/home/pablo/.cache/puppeteer/chrome/linux-153.0.8010.36/chrome-linux64/chrome"
if not os.path.exists(CHROME_BIN):
    CHROME_BIN = "/home/pablo/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"

BASE_STYLE_LIGHT = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    margin: 0;
    padding: 0;
    background: #ffffff;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
    width: 840px;
}

.box-card {
    width: 840px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    padding: 26px 30px;
    position: relative;
    overflow: hidden;
    color: #0f172a;
}

.box-topline {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #d9381e 0%, #ea580c 50%, #0284c7 100%);
}

.box-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f1f5f9;
}

.brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #d9381e;
}

.brand-badge .circle {
    width: 8px;
    height: 8px;
    background: #d9381e;
    border-radius: 50%;
}

.tag-badge {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 10.5px;
    font-weight: 700;
    color: #475569;
    letter-spacing: 0.5px;
}

.box-title {
    font-size: 20px;
    font-weight: 800;
    line-height: 1.3;
    color: #0f172a;
    margin-bottom: 4px;
    letter-spacing: -0.3px;
}

.box-subtitle {
    font-size: 12.5px;
    color: #64748b;
    line-height: 1.45;
    margin-bottom: 18px;
}

.box-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 18px;
    padding-top: 12px;
    border-top: 1px solid #f1f5f9;
    font-size: 11px;
    color: #94a3b8;
}

.footer-source {
    font-weight: 500;
}
.footer-logo {
    font-weight: 800;
    color: #d9381e;
    letter-spacing: 0.5px;
}
"""

CUADROS_ANIMADOS = {
    # 0. CARRUSEL PRINCIPAL BLANCO MATE (Cabecera del Reportaje)
    "carrusel_curaco_blanco_mate": {
        "title": "Radiografía Visual del Fiasco de Curaco: 4 Ejes Clave",
        "subtitle": "Síntesis interactiva de los hallazgos documentales, judiciales, financieros y ambientales de Última Prensa.",
        "badge": "DOSSIER MULTIMEDIA • ROTACIÓN CONTINUA",
        "source": "Segundo Juzgado de Letras de Osorno, Corte Suprema, CGR, Mercado Público y Sernageomin.",
        "width": 840,
        "height": 550,
        "steps": [
            {
                "active_idx": 0,
                "html": """
                <div style="background: #fff5f5; border: 1px solid #fed7d7; border-left: 5px solid #d9381e; padding: 18px; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 800; color: #d9381e; text-transform: uppercase;">EJE 1 • GEOLOGÍA SILENCIADA (2007 - 2016)</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #d9381e; font-weight: 700;">5 Alertas Ocultadas</span>
                    </div>
                    <h3 style="font-size: 16px; font-weight: 800; color: #9b2c2c; margin-bottom: 8px;">El Estado Sabía que el Terreno era Inviable antes de Licitar</h3>
                    <p style="font-size: 13px; color: #2d3748; line-height: 1.5;">
                        El informe de Arcadis de marzo de 2007 advirtió severas restricciones por suelos alofánicos. El Municipio ocultó el estudio en las bases de 2014. En el primer mes de faenas, la ladera oeste colapsó con una grieta de 100 metros. Los peritajes de IDOM y Petrus probaron reptación continua (*creep*) de hasta 3 metros.
                    </p>
                </div>
                """
            },
            {
                "active_idx": 1,
                "html": """
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; padding: 18px; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 800; color: #16a34a; text-transform: uppercase;">EJE 2 • EL CATALIZADOR JUDICIAL (2019 - 2021)</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #16a34a; font-weight: 700;">Decreto N° 300 • Cons. 72°</span>
                    </div>
                    <h3 style="font-size: 16px; font-weight: 800; color: #14532d; margin-bottom: 8px;">El Término Anticipado que Selló la Condena de $3.177 Millones</h3>
                    <p style="font-size: 13px; color: #2d3748; line-height: 1.5;">
                        Durante el juicio civil, el alcalde Jaime Bertín dictó el Decreto Alcaldicio N° 300 para liquidar unilateralmente el contrato. El juez sentenció que la maniobra vulneró la jurisdicción y probó que la Municipalidad «no tiene ánimo de cumplir», forzando la resolución civil del contrato bajo el Art. 1489 del Código Civil.
                    </p>
                </div>
                """
            },
            {
                "active_idx": 2,
                "html": """
                <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 5px solid #0284c7; padding: 18px; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 800; color: #0284c7; text-transform: uppercase;">EJE 3 • EL NEGOCIO DE LA BASURA (2022 - 2024)</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #0284c7; font-weight: 700;">$24.000 Millones • RUT 76.377.430-9</span>
                    </div>
                    <h3 style="font-size: 16px; font-weight: 800; color: #1e3a8a; margin-bottom: 8px;">De la Indemnización de $1.480M al Megacontrato Quinquenal</h3>
                    <p style="font-size: 13px; color: #2d3748; line-height: 1.5;">
                        Tras transar $1.480 millones en la Corte Suprema, el Municipio adjudicó a Servitrans el contrato de basura domiciliaria por casi $24.000 millones. A 9 días de comenzar las faenas, la compañía cambió su nombre a «Ciudad Limpia», sociedad hoy querellada por el SII por presuntas facturas falsas.
                    </p>
                </div>
                """
            },
            {
                "active_idx": 3,
                "html": """
                <div style="background: #fffbeb; border: 1px solid #fde68a; border-left: 5px solid #d97706; padding: 18px; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 800; color: #d97706; text-transform: uppercase;">EJE 4 • LA PARADOJA DE 2026 (ACTUALIDAD)</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #d97706; font-weight: 700;">Drenaje 200.000 m³ • Art. 25 ter</span>
                    </div>
                    <h3 style="font-size: 16px; font-weight: 800; color: #78350f; margin-bottom: 8px;">Vaciar una Fosa no Altera la Constitución Geológica del Suelo</h3>
                    <p style="font-size: 13px; color: #2d3748; line-height: 1.5;">
                        Las autoridades anuncian una inversión de US$31 millones asegurando que el terreno es apto tras vaciar 200.000 m³ con motobombas. Los expertos advierten que con las lluvias del invierno las capas freáticas volverán a licuar el suelo alofánico, además del riesgo de caducidad legal de la RCA bajo la Ley N° 19.300.
                    </p>
                </div>
                """
            }
        ]
    },

    # 1. ALERTAS GEOTÉCNICAS OCULTADAS (Sección 1 - Reemplaza tarjeta_1)
    "anim_1_alertas_geotecnicas_mate": {
        "title": "Las 5 Alertas Geotécnicas Desoídas por la Autoridad (2007 - 2017)",
        "subtitle": "La cronología pericial y judicial que demostró que el Estado licitó a sabiendas de la inviabilidad del suelo.",
        "badge": "CRONOLOGÍA PERICIAL • SECCIÓN 1",
        "source": "Sentencia Segundo Juzgado de Letras de Osorno (Rol C-351-2019), Arcadis, IDOM y Petrus.",
        "width": 840,
        "height": 550,
        "steps": [
            {
                "active_idx": 0,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #fff5f5; border: 1px solid #fecaca; border-left: 4px solid #dc2626; padding: 12px 16px; border-radius: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: #dc2626;">1. MARZO 2007 • INFORME ARCADIS (MUNICIPALIDAD)</span>
                        <p style="font-size: 12.5px; color: #1e293b; margin-top: 2px;">Concluye que el área presenta <strong>suelos alofánicos altamente plásticos</strong> y desaconseja obras sin drenajes profundos. El Municipio lo pagó y lo guardó bajo siete llaves.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">2. AGOSTO 2014 • INFORME LAB-SUR LTDA. (LICITADO)</span>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">3. NOVIEMBRE 2014 • COLAPSO LADERA OESTE (FAENA)</span>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">4. JUNIO 2016 • PERITAJE PETRUS (DEFORMACIÓN POR CREEP)</span>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">5. ENERO 2017 • VALIDACIÓN ITO MUNICIPAL (MEMO N° 003)</span>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 1,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.6;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">1. MARZO 2007 • INFORME ARCADIS (MUNICIPALIDAD)</span>
                    </div>
                    <div style="background: #fff5f5; border: 1px solid #fecaca; border-left: 4px solid #dc2626; padding: 12px 16px; border-radius: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: #dc2626;">2. AGOSTO 2014 • INFORME LAB-SUR LTDA. (LICITADO)</span>
                        <p style="font-size: 12.5px; color: #1e293b; margin-top: 2px;">El Municipio licitó basándose únicamente en Lab-Sur: 15 calicatas superficiales que <strong>no consideraron análisis de estabilidad de taludes</strong> ni la profundidad freática real.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">3. NOVIEMBRE 2014 • COLAPSO LADERA OESTE (FAENA)</span>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">4. JUNIO 2016 • PERITAJE PETRUS (DEFORMACIÓN POR CREEP)</span>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">5. ENERO 2017 • VALIDACIÓN ITO MUNICIPAL (MEMO N° 003)</span>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 2,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.6;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">1. MARZO 2007 • INFORME ARCADIS</span>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.6;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">2. AGOSTO 2014 • INFORME LAB-SUR LTDA.</span>
                    </div>
                    <div style="background: #fff5f5; border: 1px solid #fecaca; border-left: 4px solid #dc2626; padding: 12px 16px; border-radius: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: #dc2626;">3. NOVIEMBRE 2014 • COLAPSO LADERA OESTE (FAENA)</span>
                        <p style="font-size: 12.5px; color: #1e293b; margin-top: 2px;">A 20 días de iniciar excavaciones para el primer alvéolo, la ladera cedió con una <strong>grieta de 100 metros en medialuna</strong>. IDOM constató falla geológica activa.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">4. JUNIO 2016 • PERITAJE PETRUS (DEFORMACIÓN POR CREEP)</span>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">5. ENERO 2017 • VALIDACIÓN ITO MUNICIPAL (MEMO N° 003)</span>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 3,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.6;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">1. ARCADIS (2007) • 2. LAB-SUR (2014) • 3. COLAPSO (2014)</span>
                    </div>
                    <div style="background: #fff5f5; border: 1px solid #fecaca; border-left: 4px solid #dc2626; padding: 12px 16px; border-radius: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: #dc2626;">4. JUNIO 2016 • PERITAJE PETRUS (DEFORMACIÓN POR CREEP)</span>
                        <p style="font-size: 12.5px; color: #1e293b; margin-top: 2px;">Petrus comprueba desplazamiento continuo de <strong>0,5 a 3 metros</strong> por reptación plástica (*creep*) y declara que el diseño municipal se contraponía a la literatura científica.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">5. ENERO 2017 • VALIDACIÓN ITO MUNICIPAL (MEMO N° 003)</span>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 4,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 16px; border-radius: 8px; opacity: 0.6;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">ALERTAS 1 A 4: ARCADIS, LAB-SUR, COLAPSO Y PERITAJE PETRUS</span>
                    </div>
                    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; padding: 12px 16px; border-radius: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: #16a34a;">5. ENERO 2017 • VALIDACIÓN ITO MUNICIPAL (MEMO N° 003/2017-B)</span>
                        <p style="font-size: 12.5px; color: #14532d; margin-top: 2px;">El supervisor municipal <strong>Mario Mora Mora</strong> valida en terreno a Petrus y estampa que el proyecto licitado por el Municipio <strong>no cubría las necesidades técnicas y era inviable</strong>.</p>
                    </div>
                </div>
                """
            }
        ]
    },

    # 2. PANEL CIENTÍFICO Y TESTIMONIOS (Sección 1)
    "anim_2_alerta_cientifica_expertos": {
        "title": "La Verdad Científica Frente al Tribunal: 4 Voces Clave",
        "subtitle": "Los testimonios periciales que desnudaron la manipulación geológica y pluviométrica del proyecto municipal.",
        "badge": "EVIDENCIA TÉCNICA Y TESTIMONIAL",
        "source": "Expediente Rol C-351-2019, peritajes CYD, IDOM, Petrus y Sernageomin.",
        "width": 840,
        "height": 550,
        "steps": [
            {
                "active_idx": 0,
                "html": """
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                    <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-top: 3px solid #0284c7; padding: 14px; border-radius: 8px;">
                        <div style="font-size: 11px; font-weight: 800; color: #0369a1; margin-bottom: 4px;">ING. CARLOS JARAMILLO (CYD)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 700; color: #0284c7; margin-bottom: 4px;">Fraude Pluviométrico</div>
                        <p style="font-size: 12px; color: #1e3a8a; line-height: 1.45;">
                            El diseño de GHD-SIGA calculó lagunas para <strong>600 mm de lluvia al año</strong>, cuando en Osorno precipitan <strong>1.280 a 1.400 mm</strong>. Las lagunas de lixiviados habrían rebasado en el primer invierno.
                        </p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">ING. GINO RIVERA (IDOM)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">Grieta en Medialuna</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Constató falla activa de ladera y ausencia de análisis de taludes para 40 metros de altura de basura.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">ING. ANTONIO BARRIOS (PETRUS)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">Demolición de Lab-Sur</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Declaró que el estudio municipal se contraponía a todos los fundamentos de la literatura científica.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">OFICINA TÉCNICA SERNAGEOMIN</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">24 Oficios Preventivos</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Advirtió entre 2005 y 2008 que la cuenca albergaba acuíferos vulnerables y riesgo de remoción en masa.</p>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 1,
                "html": """
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">ING. CARLOS JARAMILLO (CYD)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">Fraude Pluviométrico</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Lagunas subdimensionadas a menos de la mitad del volumen de lluvias reales.</p>
                    </div>
                    <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-top: 3px solid #0284c7; padding: 14px; border-radius: 8px;">
                        <div style="font-size: 11px; font-weight: 800; color: #0369a1; margin-bottom: 4px;">ING. GINO RIVERA (IDOM)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 700; color: #0284c7; margin-bottom: 4px;">Grieta en Medialuna</div>
                        <p style="font-size: 12px; color: #1e3a8a; line-height: 1.45;">
                            Constató el <strong>deslizamiento activo de la ladera oeste</strong> y la ausencia total de análisis de taludes, recomendando perforar al menos dos pozos profundos inmediatos.
                        </p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">ING. ANTONIO BARRIOS (PETRUS)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">Demolición de Lab-Sur</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Estudio municipal sin sustento científico y fundado en contradicciones geotécnicas.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">OFICINA TÉCNICA SERNAGEOMIN</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">24 Oficios Preventivos</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Historial de advertencias oficiales desatendidas por GORE e Intendencia.</p>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 2,
                "html": """
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">ING. CARLOS JARAMILLO (CYD)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">Fraude Pluviométrico</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Lagunas subdimensionadas a menos de la mitad del volumen real.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">ING. GINO RIVERA (IDOM)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">Grieta en Medialuna</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Deslizamiento activo de la ladera oeste comprobado en terreno.</p>
                    </div>
                    <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-top: 3px solid #0284c7; padding: 14px; border-radius: 8px;">
                        <div style="font-size: 11px; font-weight: 800; color: #0369a1; margin-bottom: 4px;">ING. ANTONIO BARRIOS (PETRUS)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 700; color: #0284c7; margin-bottom: 4px;">Demolición de Lab-Sur</div>
                        <p style="font-size: 12px; color: #1e3a8a; line-height: 1.45;">
                            Demolió el informe de Lab-Sur: <em>«Contenía conclusiones equivocadas que se contraponen con los fundamentos de la literatura científica de la mecánica de suelos»</em>.
                        </p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">OFICINA TÉCNICA SERNAGEOMIN</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">24 Oficios Preventivos</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Historial de advertencias oficiales desatendidas por GORE e Intendencia.</p>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 3,
                "html": """
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">ING. CARLOS JARAMILLO (CYD)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">Fraude Pluviométrico</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Lagunas subdimensionadas a menos de la mitad del volumen real.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">ING. GINO RIVERA (IDOM)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">Grieta en Medialuna</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Deslizamiento activo de ladera comprobado en terreno.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">ING. ANTONIO BARRIOS (PETRUS)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">Demolición de Lab-Sur</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Estudio municipal sin rigor científico.</p>
                    </div>
                    <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-top: 3px solid #0284c7; padding: 14px; border-radius: 8px;">
                        <div style="font-size: 11px; font-weight: 800; color: #0369a1; margin-bottom: 4px;">OFICINA TÉCNICA SERNAGEOMIN</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; font-weight: 700; color: #0284c7; margin-bottom: 4px;">24 Oficios Preventivos</div>
                        <p style="font-size: 12px; color: #1e3a8a; line-height: 1.45;">
                            Los 24 informes emitidos entre 2005 y 2008 advertían que la cuenca de Osorno albergaba <strong>acuíferos de altísima vulnerabilidad hidrogeológica</strong> e inestabilidad geomecánica.
                        </p>
                    </div>
                </div>
                """
            }
        ]
    },

    # 3. EL CATALIZADOR DEL DECRETO 300 (Sección 2)
    "anim_3_catalizador_decreto300": {
        "title": "El Decreto N° 300: El Autogolpe que Sentenció la Derrota Municipal",
        "subtitle": "Cómo la decisión unilateral de Jaime Bertín en 2020 invadió la justicia ordinaria y forzó la condena de $3.177 millones.",
        "badge": "ANÁLISIS PROCESAL • CONSIDERANDOS 72° Y 73°",
        "source": "Segundo Juzgado de Letras de Osorno (Rol C-351-2019) y Corte de Apelaciones de Valdivia.",
        "width": 840,
        "height": 550,
        "steps": [
            {
                "active_idx": 0,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #fff5f5; border: 1px solid #cbd5e1; border-left: 4px solid #b91c1c; padding: 14px 18px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 11px; font-weight: 800; color: #b91c1c; text-transform: uppercase;">1. EL ACTO MUNICIPAL (10/01/2020)</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b;">Decreto Alcaldicio N° 300</span>
                        </div>
                        <p style="font-size: 13px; color: #1e293b; line-height: 1.5;">
                            El alcalde <strong>Jaime Bertín</strong> decreta el término anticipado del contrato con Servitrans y ordena liquidar la obra, ordenando ejecutar boletas y pólizas de garantía por <strong>$353 millones</strong> y <strong>19.209 UF</strong>.
                        </p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 12px 18px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">2. VULNERACIÓN DE LA JURISDICCIÓN (CONSIDERANDO 72°)</span>
                        <p style="font-size: 12.5px; color: #64748b; margin-top: 4px;">Al estar el litigio ya en tribunales, la Administración no podía resolver el contrato unilateralmente.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 12px 18px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">3. EL EFECTO JUDICIAL INAPELABLE (CONSIDERANDO 73°)</span>
                        <p style="font-size: 12.5px; color: #64748b; margin-top: 4px;">El juez acreditó el incumplimiento culpable de la Municipalidad y ordenó pagar $3.177 millones.</p>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 1,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 12px 18px; border-radius: 8px; opacity: 0.7;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">1. EL ACTO MUNICIPAL (10/01/2020)</span>
                        <p style="font-size: 12.5px; color: #475569; margin-top: 2px;">Decreto N° 300 decreta término anticipado unilateral para eludir responsabilidad contractual.</p>
                    </div>
                    <div style="background: #fff5f5; border: 1px solid #fecaca; border-left: 4px solid #dc2626; padding: 14px 18px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 11px; font-weight: 800; color: #dc2626; text-transform: uppercase;">2. VULNERACIÓN DE LA JURISDICCIÓN (CONS. 72°)</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #dc2626; font-weight: 700;">Art. 1546 Código Civil</span>
                        </div>
                        <p style="font-size: 13px; color: #7f1d1d; line-height: 1.5;">
                            <em>«Palmario resulta indicar que dicho decreto se dictó durante la sustanciación del juicio, vulnerando expresamente la esfera de este Juez... confirma que la demandada <strong style='text-decoration: underline;'>no tiene ánimo de cumplir sus obligaciones</strong>».</em>
                        </p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 12px 18px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">3. EL EFECTO JUDICIAL INAPELABLE (CONSIDERANDO 73°)</span>
                        <p style="font-size: 12.5px; color: #64748b; margin-top: 4px;">El juez acreditó el incumplimiento culpable de la Municipalidad y ordenó pagar $3.177 millones.</p>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 2,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 12px 18px; border-radius: 8px; opacity: 0.7;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">1. EL ACTO MUNICIPAL (10/01/2020)</span>
                        <p style="font-size: 12.5px; color: #475569; margin-top: 2px;">Decreto N° 300 decreta término anticipado unilateral para eludir responsabilidad contractual.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 12px 18px; border-radius: 8px; opacity: 0.7;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">2. VULNERACIÓN DE LA JURISDICCIÓN (CONS. 72°)</span>
                        <p style="font-size: 12.5px; color: #475569; margin-top: 2px;">La invasión de competencias exclusivas del tribunal destruyó toda la defensa procesal de la IMO.</p>
                    </div>
                    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; padding: 14px 18px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 11px; font-weight: 800; color: #16a34a; text-transform: uppercase;">3. SENTENCIA DEFINITIVA (CONS. 73° Y RESOLUTIVO)</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #16a34a; font-weight: 700;">Art. 1489 Código Civil</span>
                        </div>
                        <p style="font-size: 13px; color: #14532d; line-height: 1.5;">
                            Se acoge la demanda de Servitrans por culpa exclusiva del Municipio: resolución del contrato y condena a pagar <strong>$3.177.732.167 de pesos</strong> por daño emergente ($1.992M) y lucro cesante ($1.113M).
                        </p>
                    </div>
                </div>
                """
            }
        ]
    },

    # 4. LIQUIDACIÓN EN TRIBUNALES (Sección 2 - Reemplaza tarjeta_2)
    "anim_4_liquidacion_tribunales_mate": {
        "title": "La Liquidación Judicial del Fiasco: Del Fallo al Finiquito",
        "subtitle": "Cómo la condena civil de $3.177 millones derivó en el acuerdo de $1.480 millones en la Corte Suprema.",
        "badge": "DESGLOSE PATRIMONIAL • SECCIÓN 2",
        "source": "Sentencia C-351-2019, Corte de Valdivia y Acta N° 1067_28 del Concejo Municipal.",
        "width": 840,
        "height": 550,
        "steps": [
            {
                "active_idx": 0,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #fff5f5; border: 1px solid #fecaca; border-left: 4px solid #dc2626; padding: 14px 18px; border-radius: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: #dc2626;">PASO 1 • CONDENA EN PRIMERA INSTANCIA (10/06/2020)</span>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 800; color: #991b1b; margin: 4px 0;">$3.177.732.167 CLP</div>
                        <p style="font-size: 12.5px; color: #1e293b; line-height: 1.45;">Desglosado en: <strong>$1.992.918.300</strong> por daño emergente (gastos generales por 4 años de faenas paralizadas), <strong>$1.113.638.978</strong> por lucro cesante y <strong>$71.174.889</strong> en retenciones.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 18px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">PASO 2 • RATIFICACIÓN CORTE DE VALDIVIA (12/08/2021)</span>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 18px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">PASO 3 • ACUERDO EN CORTE SUPREMA (30/05/2022)</span>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 1,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 18px; border-radius: 8px; opacity: 0.6;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">PASO 1 • CONDENA EN PRIMERA INSTANCIA ($3.177M)</span>
                    </div>
                    <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #0284c7; padding: 14px 18px; border-radius: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: #0284c7;">PASO 2 • RATIFICACIÓN CORTE DE VALDIVIA (12/08/2021)</span>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 800; color: #0369a1; margin: 4px 0;">Confirma en Todas sus Partes (Rol 561-2020)</div>
                        <p style="font-size: 12.5px; color: #1e3a8a; line-height: 1.45;">Los ministros Correa Rosado y Vidal Etcheverry establecen que el Municipio violó la <strong>buena fe</strong> (Art. 1546 CC) y el <strong>equilibrio económico</strong> (Ley N° 18.575).</p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 10px 18px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">PASO 3 • ACUERDO EN CORTE SUPREMA (30/05/2022)</span>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 2,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 18px; border-radius: 8px; opacity: 0.6;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">PASO 1 • CONDENA $3.177M • PASO 2 • RATIFICACIÓN VALDIVIA</span>
                    </div>
                    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; padding: 14px 18px; border-radius: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: #16a34a;">PASO 3 • ACUERDO EN CORTE SUPREMA (30/05/2022)</span>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 800; color: #15803d; margin: 4px 0;">$1.480.000.000 + Devolución Boleta $360M</div>
                        <p style="font-size: 12.5px; color: #14532d; line-height: 1.45;">Concejo aprueba pago al contado para evitar embargo por más de $4.000M. Servitrans se retira con más de $6.300M sumando anticipos previos.</p>
                    </div>
                </div>
                """
            }
        ]
    },

    # 5. EL NEGOCIO DE LA BASURA Y MUTACIÓN A CIUDAD LIMPIA (Sección 3 - Reemplaza tarjeta_3)
    "anim_5_desglose_financiero_mate": {
        "title": "El Giro Corporativo: De la Condena Judicial al Megacontrato de la Basura",
        "subtitle": "La metamorfosis financiera: cómo Servitrans pasó de cobrar una indemnización a adjudicarse $24.000 millones.",
        "badge": "FLUJO DE FONDOS Y RED SOCIETARIA",
        "source": "Mercado Público (ID 2308-97-LR23), Registro de Empresas y Sociedades y querella SII.",
        "width": 840,
        "height": 550,
        "steps": [
            {
                "active_idx": 0,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #fff5f5; border: 1px solid #fed7d7; border-left: 4px solid #b91c1c; padding: 14px 18px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 11px; font-weight: 800; color: #b91c1c;">1. INDEMNIZACIÓN JUDICIAL (MAYO 2022)</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 800; color: #b91c1c;">$1.480.000.000</span>
                        </div>
                        <p style="font-size: 12.5px; color: #2d3748; margin-top: 4px;">Finiquito judicial aprobado por el Concejo Municipal en pago único para cerrar la demanda de Curaco.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 12px 18px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">2. MEGACONTRATO LICITACIÓN BASURA (NOVIEMBRE 2023)</span>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #94a3b8; margin-top: 2px;">$23.963.982.000 CLP (60 meses)</div>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 12px 18px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">3. MUTACIÓN SOCIETARIA Y QUERELLA DEL SII (2024 - 2025)</span>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 1,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 18px; border-radius: 8px; opacity: 0.6;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">1. INDEMNIZACIÓN JUDICIAL: $1.480M EN EFECTIVO</span>
                    </div>
                    <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #0284c7; padding: 14px 18px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 11px; font-weight: 800; color: #0284c7;">2. MEGACONTRATO LICITACIÓN BASURA (NOV 2023)</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 800; color: #0284c7;">$23.963.982.000</span>
                        </div>
                        <p style="font-size: 12.5px; color: #1e3a8a; margin-top: 4px;">Apenas 13 meses después, el Municipio adjudica a Servitrans la recolección de basura domiciliaria por <strong>$399.399.700 mensuales</strong> durante 5 años.</p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 12px 18px; border-radius: 8px; opacity: 0.5;">
                        <span style="font-size: 11px; font-weight: 700; color: #94a3b8;">3. MUTACIÓN SOCIETARIA Y QUERELLA DEL SII (2024 - 2025)</span>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 2,
                "html": """
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 18px; border-radius: 8px; opacity: 0.6;">
                        <span style="font-size: 11px; font-weight: 700; color: #64748b;">1. INDEMNIZACIÓN $1.480M • 2. MEGACONTRATO $23.964M</span>
                    </div>
                    <div style="background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #d97706; padding: 14px 18px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 11px; font-weight: 800; color: #d97706;">3. MUTACIÓN A «CIUDAD LIMPIA» Y QUERELLA SII (2024-2025)</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: #b45309;">RUT 76.377.430-9</span>
                        </div>
                        <p style="font-size: 12.5px; color: #78350f; margin-top: 4px;">A 9 días de debutar, Servitrans muta su razón social a «Ciudad Limpia». En 2025, el SII se querella criminalmente por presunto uso reiterado de facturas falsas.</p>
                    </div>
                </div>
                """
            }
        ]
    },

    # 6. PARADOJA DE 2026: DRENAJE VS SUELO ALOFÁNICO (Sección 4 - Reemplaza tarjeta_4)
    "anim_6_paradoja_suelo_2026": {
        "title": "La Paradoja de 2026: Drenar 200.000 m³ no Cambia la Geología",
        "subtitle": "El artificio mecánico de motobombas frente a la licuefacción alofánica y el riesgo legal de la RCA.",
        "badge": "ANÁLISIS TÉCNICO Y AMBIENTAL",
        "source": "Subdere, GORE Los Lagos, SMA y Ley N° 19.300 sobre Bases Generales del Medio Ambiente.",
        "width": 840,
        "height": 550,
        "steps": [
            {
                "active_idx": 0,
                "html": """
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px;">
                    <div style="background: #fffbeb; border: 1px solid #fde68a; border-top: 3px solid #d97706; padding: 16px; border-radius: 8px;">
                        <div style="font-size: 11px; font-weight: 800; color: #b45309; margin-bottom: 4px;">EL ANUNCIO OFICIAL (JULIO 2026)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 800; color: #92400e; margin-bottom: 6px;">«Terreno 100 % Apto»</div>
                        <p style="font-size: 12px; color: #78350f; line-height: 1.45;">
                            El GORE y alcaldes instalan motobombas para vaciar <strong>200.000 m³ de agua</strong> acumulada y afirman que el suelo no reviste ningún riesgo estructural, proyectando un megaproyecto de <strong>US$31 millones</strong>.
                        </p>
                    </div>
                    <div style="background: #ffffff; border: 1px dashed #e2e8f0; padding: 16px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">LA REALIDAD GEOMECÁNICA</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 6px;">Suelos Alofánicos</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">El agua subterránea licúa el suelo desde las napas. En invierno volverá a deslizarse inexorablemente.</p>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 1,
                "html": """
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px;">
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; opacity: 0.6;">
                        <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px;">EL ANUNCIO OFICIAL (JULIO 2026)</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 6px;">«Terreno Apto»</div>
                        <p style="font-size: 12px; color: #64748b; line-height: 1.45;">Vaciado de 200.000 m³ con bombas industriales en otoño.</p>
                    </div>
                    <div style="background: #fff5f5; border: 1px solid #fecaca; border-top: 3px solid #dc2626; padding: 16px; border-radius: 8px;">
                        <div style="font-size: 11px; font-weight: 800; color: #dc2626; margin-bottom: 4px;">LA REALIDAD GEOMECÁNICA</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 800; color: #991b1b; margin-bottom: 6px;">Licuefacción y Colapso</div>
                        <p style="font-size: 12px; color: #7f1d1d; line-height: 1.45;">
                            La inestabilidad no proviene de la lluvia superficial: <strong>las capas freáticas subterráneas saturan los suelos alofánicos perdiendo toda cohesión</strong>. En el invierno austral, la masa de tierra volverá a colapsar.
                        </p>
                    </div>
                </div>
                """
            },
            {
                "active_idx": 2,
                "html": """
                <div style="background: #fff5f5; border: 1px solid #fecaca; border-left: 5px solid #dc2626; padding: 16px; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 11px; font-weight: 800; color: #dc2626; text-transform: uppercase;">RIESGO NORMATIVO INSALVABLE • LEY N° 19.300</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #dc2626; font-weight: 700;">Artículo 25 ter</span>
                    </div>
                    <h3 style="font-size: 15px; font-weight: 800; color: #7f1d1d; margin-bottom: 6px;">Caducidad Inminente de la Resolución de Calificación Ambiental (RCA)</h3>
                    <p style="font-size: 12.5px; color: #1e293b; line-height: 1.5;">
                        La RCA original otorgada hace más de una década se encuentra formalmente expuesta a la <strong>caducidad legal</strong>: el Art. 25 ter de la Ley de Bases del Medio Ambiente sanciona con pérdida de vigencia a aquellos proyectos cuyas obras de inicio material hayan estado <strong>paralizadas por más de 5 años consecutivos</strong>.
                    </p>
                </div>
                """
            }
        ]
    }
}


def render_animated_cards(output_dir: Path):
    """Renderiza los cuadros claros/mate en secuencias de fotogramas y los compila a GIF y WebP."""
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "temp_html"
    temp_dir.mkdir(parents=True, exist_ok=True)

    for card_key, data in CUADROS_ANIMADOS.items():
        print(f"\nProcesando cuadro animado claro: {card_key}...")
        step_pngs = []

        # 1. Renderizar cada fotograma/paso
        for idx, step in enumerate(data["steps"]):
            step_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
{BASE_STYLE_LIGHT}
</style>
</head>
<body>
<div class="box-card">
    <div class="box-topline"></div>
    <div class="box-header">
        <div class="brand-badge">
            <span class="circle"></span>
            ÚLTIMA PRENSA • INVESTIGACIÓN JUDICIAL
        </div>
        <div class="tag-badge">{data['badge']}</div>
    </div>
    <h2 class="box-title">{data['title']}</h2>
    <p class="box-subtitle">{data['subtitle']}</p>
    
    <div class="box-content">
        {step['html']}
    </div>

    <div class="box-footer">
        <div class="footer-source">⚖️ Fuente: {data['source']}</div>
        <div class="footer-logo">CURACO: EL NEGOCIO DE LA BASURA</div>
    </div>
</div>
</body>
</html>"""
            html_file = temp_dir / f"{card_key}_step_{idx}.html"
            png_file = temp_dir / f"{card_key}_step_{idx}.png"

            with open(html_file, "w", encoding="utf-8") as f:
                f.write(step_html)

            # Usamos screenshot exacto con viewport recortado
            cmd = [
                CHROME_BIN,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--force-device-scale-factor=2",
                f"--window-size={data['width']},{data['height']}",
                f"--screenshot={png_file}",
                f"file://{html_file.resolve()}"
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            step_pngs.append(png_file)

        # 2. Compilar animación en bucle con FFmpeg (WebP y GIF)
        list_file = temp_dir / f"{card_key}_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for p in step_pngs:
                # Cada paso se muestra 2.8 segundos para lectura ágil y fluida
                f.write(f"file '{p.resolve()}'\nduration 2.8\n")
            f.write(f"file '{step_pngs[-1].resolve()}'\n")

        gif_out = output_dir / f"{card_key}.gif"
        webp_out = output_dir / f"{card_key}.webp"

        # GIF animado claro con loop infinito garantizado
        cmd_gif = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file.resolve()),
            "-vf", "fps=4,scale=840:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
            "-loop", "0",
            str(gif_out.resolve())
        ]
        subprocess.run(cmd_gif, check=True, capture_output=True)
        print(f"  ✓ {gif_out.name} generado con éxito ({gif_out.stat().st_size // 1024} KB)")

        # WebP animado claro
        cmd_webp = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file.resolve()),
            "-vf", "fps=4,scale=840:-1:flags=lanczos",
            "-loop", "0", "-c:v", "libwebp", "-lossless", "0", "-q:v", "90",
            str(webp_out.resolve())
        ]
        subprocess.run(cmd_webp, check=True, capture_output=True)
        print(f"  ✓ {webp_out.name} generado con éxito ({webp_out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    out = Path("reportajes/caso_relleno_curaco_osorno/graficos")
    render_animated_cards(out)
    print("\nProceso de animación en fondo blanco/mate finalizado con éxito.")
