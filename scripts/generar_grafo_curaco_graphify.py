#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del Grafo de Conocimiento Pericial: Caso Caducidad RCA Curaco
Utiliza la suite oficial Graphify (build, cluster, analyze, report, export)
para mapear la red de actores, contradicciones técnicas, fraude administrativo
y pasivos ambientales del Relleno Sanitario Curaco (Osorno).
"""

import sys
import json
from pathlib import Path

# Importar Graphify desde el entorno del tool
try:
    import networkx as nx
    from graphify import build, cluster, analyze, report, export
except ImportError:
    print("[!] Error: Graphify no está instalado en este entorno Python.")
    print("    Ejecutar con: /home/pablo/.local/share/uv/tools/graphifyy/bin/python")
    sys.exit(1)

OUT_DIR = Path("reportajes/caso_caducidad_rca_curaco/graphify-out")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Definición estructurada de Nodos, Aristas e Hiperaristas
nodes = [
    # Actores Institucionales y Políticos
    {
        "id": "actor_sea_los_lagos",
        "label": "Servicio de Evaluación Ambiental (SEA Los Lagos)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md",
        "rationale": "Órgano competente que otorgó la RCA N° 43/2010 y convalidó fraudulentamente el inicio de obras mediante Res. Ex. N° 1697/2015 omitiendo la caducidad legal."
    },
    {
        "id": "actor_sma",
        "label": "Superintendencia del Medio Ambiente (SMA)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md",
        "rationale": "Órgano fiscalizador con falta de servicio por omisión prolongada al no constatar la paralización total de obras desde octubre de 2015."
    },
    {
        "id": "actor_mun_osorno",
        "label": "I. Municipalidad de Osorno (Titular RCA)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2010-01-26_DOC_85_Servicio_Evaluación_Ambiental__X_Región_de_Los_Lagos_Resolución_de_calificación_ambiental__RCA.md",
        "rationale": "Titular del proyecto que ocultó los estudios de suelo a la contratista y paralizó las faenas por Decreto N° 9.393/2015."
    },
    {
        "id": "actor_jaime_bertin",
        "label": "Jaime Bertín Valenzuela (Exalcalde de Osorno)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md",
        "rationale": "Firmó el Ord. N° 070 simulando continuidad de faenas en enero 2015 y decretó la paralización total indefinida en octubre 2015."
    },
    {
        "id": "actor_asoc_municipios",
        "label": "Asociación de Municipios Provincia de Osorno",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md",
        "rationale": "Entidad coordinadora política que busca reflotar el proyecto como Centro de Tratamiento Integral sobre la misma RCA caduca."
    },
    {
        "id": "actor_subdere_gore",
        "label": "Subdere y GORE Los Lagos",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md",
        "rationale": "Entidades gubernamentales que financian consultorías y presionan por mantener viva la RCA para evitar pérdida de rentabilidad social (RS)."
    },
    {
        "id": "actor_bid",
        "label": "Banco Interamericano de Desarrollo (BID)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md",
        "rationale": "Organismo multilateral que financia el nuevo proyecto (USD $31 millones), condicionado al cumplimiento del Marco de Salvaguardas ESPS."
    },
    {
        "id": "actor_servitrans",
        "label": "Consorcio Servitrans Osorno S.A.",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/06_sentencia_corte_valdivia_servitrans_vs_municipalidad.md",
        "rationale": "Contratista que demandó la resolución de contrato por negligencia municipal y obtuvo indemnización ratificada por la Corte Suprema."
    },
    {
        "id": "actor_arcadis",
        "label": "Arcadis Chile S.A. (Consultora Geotécnica)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/07_analisis_informe_arcadis_inviabilidad_relleno.md",
        "rationale": "Consultora internacional que emitió los informes de 2015 determinando la inviabilidad estructural de construir el relleno según la RCA."
    },
    {
        "id": "actor_corte_suprema",
        "label": "Poder Judicial (2° Juzgado, C.A. Valdivia y Corte Suprema)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md",
        "rationale": "Dictaron sentencias definitivas (Rol C-351-2019, Rol 678-2020 y Rol 69.455-2021) acreditando la culpa exclusiva municipal."
    },
    {
        "id": "actor_sernageomin",
        "label": "SERNAGEOMIN Zona Sur",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-05-11_DOC_14_SERNAGEOMIN__Zona_Sur_Oficio_pronunciamiento_con_observaciones_al_EIA.md",
        "rationale": "Exigió en 2009 red de monitoreo de aguas subterráneas y plan de contingencia ante riesgo de lixiviados."
    },
    {
        "id": "actor_dga",
        "label": "Dirección General de Aguas (DGA Los Lagos)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-05-25_DOC_17_DGA__Región_de_Los_Lagos_Oficio_pronunciamiento_con_observaciones_al_EIA.md",
        "rationale": "Advirtió sobre afloramiento de lixiviados en taludes y exigió precisión sobre la tasa de recarga y captaciones subterráneas."
    },

    # Documentos Clave e Instrumentos Jurídicos
    {
        "id": "doc_eia_original",
        "label": "EIA Relleno Sanitario Osorno (2009)",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-04-06_DOC_01_Ilustre_Municipalidad_de_Osorno_Estudio_de_impacto_ambiental_Capitulo_1._Descripción_del_Proyecto.md",
        "rationale": "Documento fundacional que aseguró que las napas estaban a más de 10 metros y fijó taludes 1:3 en suelo alofánico."
    },
    {
        "id": "doc_anexo5_geotecnico",
        "label": "Anexo 5: Estudio Geotécnico Original (EIA 2009)",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-04-06_DOC_01_Ilustre_Municipalidad_de_Osorno_Estudio_de_impacto_ambiental_Anexo_5._Estudio_Geotecnico.md",
        "rationale": "Reconoció suelo tipo MH (limo de alta compresibilidad) pero sostuvo 'sin presencia de agua' tras muestrear solo en enero seco."
    },
    {
        "id": "doc_anexo8_hidrogeologico",
        "label": "Anexo 8: Estudio Hidrogeológico (EIA 2009)",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-04-06_DOC_01_Ilustre_Municipalidad_de_Osorno_Estudio_de_impacto_ambiental_Anexo_8._Estudio_Hidrogeologico_y_calidad_del_agua.md",
        "rationale": "Afirmó falsamente que el acuífero estaba confinado a 20-23 metros y que las calicatas a 10 metros eran completamente secas."
    },
    {
        "id": "doc_estudio_agrologico",
        "label": "Estudio Agrológico (Adendas 1 y 2)",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-10-28_DOC_58_Ilustre_Municipalidad_de_Osorno_Adenda_Anexo_B._Estudio_Agrológico.md",
        "rationale": "Contradijo el estudio geotécnico admitiendo que el nivel freático está comúnmente en la superficie la mayor parte del año."
    },
    {
        "id": "doc_rca_43_2010",
        "label": "RCA N° 43/2010 (Resolución Calificación Ambiental)",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2010-01-26_DOC_85_Servicio_Evaluación_Ambiental__X_Región_de_Los_Lagos_Resolución_de_calificación_ambiental__RCA.md",
        "rationale": "Resolución aprobatoria con 20 años de vida útil (2010-2030), hoy consumida en un 83 % sin operar y caduca por Ley 19.300."
    },
    {
        "id": "doc_ord_070_bertin",
        "label": "Oficio ORD. N° 070 (21/01/2015)",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md",
        "rationale": "Oficio presentado por Jaime Bertín 5 días antes del plazo fatal para simular inicio de obras con un contrato en papel."
    },
    {
        "id": "doc_decreto_9393",
        "label": "Decreto Alcaldicio N° 9.393 (13/10/2015)",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md",
        "rationale": "Decreto municipal vinculante que suspendió total e indefinidamente todas las obras en Curaco debido a las fallas geotécnicas."
    },
    {
        "id": "doc_res_ex_1697",
        "label": "Resolución Exenta N° 1697/2015 SEA",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/02_resolucion_sea_constatacion_obras_curaco.md",
        "rationale": "Certificó un 'desarrollo sistemático e ininterrumpido' dos meses después de que el propio municipio había paralizado las obras por decreto."
    },
    {
        "id": "doc_decreto_300",
        "label": "Decreto Alcaldicio N° 300 (10/01/2020)",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/06_sentencia_corte_valdivia_servitrans_vs_municipalidad.md",
        "rationale": "Terminación unilateral del contrato de obras con Servitrans, destruyendo el único sustento fáctico de la Res. 1697."
    },
    {
        "id": "doc_sentencia_c351",
        "label": "Sentencia Definitiva Rol C-351-2019",
        "file_type": "document",
        "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/06_sentencia_corte_valdivia_servitrans_vs_municipalidad.md",
        "rationale": "Falló que el contrato se resolvió por incumplimiento culpable de la Municipalidad de Osorno por engaño en las condiciones del suelo."
    },

    # Elementos Técnicos, Geotécnicos y Ambientales
    {
        "id": "elem_alveolo_1",
        "label": "Alvéolo N° 1 (Excavación de 6 Metros)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md",
        "rationale": "Foso excavado que cortó el acuífero superficial y originó la rotura de talud en noviembre de 2014."
    },
    {
        "id": "elem_napa_freatica",
        "label": "Afloramiento de Napa Freática a 6 Metros",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md",
        "rationale": "Afloramiento hídrico constante que desmintió la cota de 20 metros del EIA y recarga permanentemente el alvéolo."
    },
    {
        "id": "elem_suelo_alofanico",
        "label": "Suelo Alofánico Trumao (Clasificación MH)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/07_analisis_informe_arcadis_inviabilidad_relleno.md",
        "rationale": "Suelo volcánico con tixotropía y pérdida drástica de resistencia al saturarse, impidiendo taludes verticales o 1:3."
    },
    {
        "id": "elem_laguna_200k",
        "label": "Laguna Artificial de 200.000 m³ de Aguas y Lixiviados",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md",
        "rationale": "Masa de agua estancada y contaminada acumulada durante una década en el alvéolo abandonado."
    },
    {
        "id": "elem_bombeo_2026",
        "label": "Evacuación por Bombeo (Abril-Mayo 2026)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md",
        "rationale": "Operación de vaciado hacia la red superficial que fracasó, verificándose por Google Earth una nueva inundación total."
    },
    {
        "id": "elem_estero_curaco_rahue",
        "label": "Cuenca Estero Curaco y Río Rahue",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-05-25_DOC_17_DGA__Región_de_Los_Lagos_Oficio_pronunciamiento_con_observaciones_al_EIA.md",
        "rationale": "Cuerpos receptores hídricos receptores de descargas y escorrentías de lixiviados del vertedero viejo y relleno colapsado."
    },
    {
        "id": "elem_inviabilidad_talud",
        "label": "Inviabilidad de Taludes 1:3 y Modificación Sustantiva",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/07_analisis_informe_arcadis_inviabilidad_relleno.md",
        "rationale": "El tendido a 1:5 o 1:6 reduce el volumen útil a la mitad y altera sustancialmente el proyecto evaluado en el EIA."
    },

    # Institutos Jurídicos y Normativos
    {
        "id": "norma_caducidad_25ter",
        "label": "Caducidad de Pleno Derecho (Art. 25 ter Ley 19.300)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md",
        "rationale": "Institución legal que extingue la RCA tras 5 años sin inicio sistemático de obras materiales."
    },
    {
        "id": "norma_falta_servicio",
        "label": "Falta de Servicio de la Administración (Art. 42 Ley 18.575)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md",
        "rationale": "Responsabilidad extracontractual del Estado por omisión culposa del SEA y la SMA al no tramitar la caducidad de oficio."
    },
    {
        "id": "norma_modificacion_sustantiva",
        "label": "Modificación Sustantiva de Proyecto (Art. 8 Ley 19.300)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md",
        "rationale": "Exige obligatoriamente el ingreso de un nuevo Estudio de Impacto Ambiental ante cambios esenciales de ingeniería."
    },
    {
        "id": "norma_consulta_indigena_pac",
        "label": "Convenio 169 OIT y Participación Ciudadana (PAC)",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md",
        "rationale": "Derechos fundamentales de las comunidades mapuche-huilliche de Curaco que se vulneran al reciclar la RCA sin consulta."
    },
    {
        "id": "norma_salvaguardas_bid",
        "label": "Marco de Salvaguardas ESPS del BID",
        "file_type": "concept",
        "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md",
        "rationale": "Normas internacionales que prohíben el financiamiento de proyectos con licencias ambientales extintas o viciadas."
    }
]

edges = [
    # Comunidad 1: La Operación de Encubrimiento Administrativo
    {"source": "actor_jaime_bertin", "target": "doc_ord_070_bertin", "relation": "emite", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},
    {"source": "doc_ord_070_bertin", "target": "actor_sea_los_lagos", "relation": "presentado_a", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},
    {"source": "actor_jaime_bertin", "target": "doc_decreto_9393", "relation": "ordena_suspension_total", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},
    {"source": "doc_decreto_9393", "target": "doc_res_ex_1697", "relation": "contradice_y_desmiente", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},
    {"source": "actor_sea_los_lagos", "target": "doc_res_ex_1697", "relation": "emite_sin_inspeccion_terreno", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},
    {"source": "actor_sea_los_lagos", "target": "norma_caducidad_25ter", "relation": "omite_aplicar_de_oficio", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},
    {"source": "actor_sma", "target": "norma_falta_servicio", "relation": "incurre_por_inaccion", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},

    # Comunidad 2: La Falla Geotécnica y la Falsedad Hidrogeológica
    {"source": "doc_eia_original", "target": "doc_anexo5_geotecnico", "relation": "incorpora", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-04-06_DOC_01_Ilustre_Municipalidad_de_Osorno_Estudio_de_impacto_ambiental_Capitulo_1._Descripción_del_Proyecto.md", "weight": 1.0},
    {"source": "doc_eia_original", "target": "doc_anexo8_hidrogeologico", "relation": "incorpora", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-04-06_DOC_01_Ilustre_Municipalidad_de_Osorno_Estudio_de_impacto_ambiental_Capitulo_1._Descripción_del_Proyecto.md", "weight": 1.0},
    {"source": "doc_anexo5_geotecnico", "target": "elem_suelo_alofanico", "relation": "identifica_tipo_MH", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-04-06_DOC_01_Ilustre_Municipalidad_de_Osorno_Estudio_de_impacto_ambiental_Anexo_5._Estudio_Geotecnico.md", "weight": 1.0},
    {"source": "doc_anexo8_hidrogeologico", "target": "elem_napa_freatica", "relation": "afirma_napa_a_20m_erroneamente", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-04-06_DOC_01_Ilustre_Municipalidad_de_Osorno_Estudio_de_impacto_ambiental_Anexo_8._Estudio_Hidrogeologico_y_calidad_del_agua.md", "weight": 1.0},
    {"source": "doc_estudio_agrologico", "target": "doc_anexo5_geotecnico", "relation": "contradice_en_presencia_agua", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-10-28_DOC_58_Ilustre_Municipalidad_de_Osorno_Adenda_Anexo_B._Estudio_Agrológico.md", "weight": 1.0},
    {"source": "actor_dga", "target": "doc_eia_original", "relation": "advierte_riesgo_afloramientos", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-05-25_DOC_17_DGA__Región_de_Los_Lagos_Oficio_pronunciamiento_con_observaciones_al_EIA.md", "weight": 1.0},
    {"source": "actor_sernageomin", "target": "doc_eia_original", "relation": "exige_monitoreo_aguas_subterraneas", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/expediente_seia_completo/markdown/2009-05-11_DOC_14_SERNAGEOMIN__Zona_Sur_Oficio_pronunciamiento_con_observaciones_al_EIA.md", "weight": 1.0},
    {"source": "elem_alveolo_1", "target": "elem_napa_freatica", "relation": "corta_y_expone", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md", "weight": 1.0},
    {"source": "elem_napa_freatica", "target": "elem_suelo_alofanico", "relation": "satura_y_licua", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md", "weight": 1.0},
    {"source": "actor_arcadis", "target": "elem_inviabilidad_talud", "relation": "dictamina_inviabilidad_1a3", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/07_analisis_informe_arcadis_inviabilidad_relleno.md", "weight": 1.0},
    {"source": "elem_inviabilidad_talud", "target": "norma_modificacion_sustantiva", "relation": "gatilla_obligatoriamente", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},

    # Comunidad 3: La Derrota Judicial y Rescisión del Contrato
    {"source": "actor_mun_osorno", "target": "doc_decreto_300", "relation": "termina_unilateralmente_contrato", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/06_sentencia_corte_valdivia_servitrans_vs_municipalidad.md", "weight": 1.0},
    {"source": "actor_servitrans", "target": "actor_mun_osorno", "relation": "demanda_por_incumplimiento_culpable", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/06_sentencia_corte_valdivia_servitrans_vs_municipalidad.md", "weight": 1.0},
    {"source": "actor_corte_suprema", "target": "doc_sentencia_c351", "relation": "ratifica_definitivamente", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},
    {"source": "doc_sentencia_c351", "target": "actor_mun_osorno", "relation": "condena_por_negligencia_grave", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/documentos/transcripciones/06_sentencia_corte_valdivia_servitrans_vs_municipalidad.md", "weight": 1.0},
    {"source": "doc_sentencia_c351", "target": "doc_res_ex_1697", "relation": "extingue_soporte_contractual", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},

    # Comunidad 4: El Pasivo Ambiental y Contaminación de la Cuenca
    {"source": "elem_alveolo_1", "target": "elem_laguna_200k", "relation": "se_convierte_en", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md", "weight": 1.0},
    {"source": "elem_laguna_200k", "target": "elem_bombeo_2026", "relation": "objeto_de", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md", "weight": 1.0},
    {"source": "elem_bombeo_2026", "target": "elem_estero_curaco_rahue", "relation": "vuelca_efluentes_en", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md", "weight": 1.0},
    {"source": "elem_napa_freatica", "target": "elem_laguna_200k", "relation": "reinunda_continuamente", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md", "weight": 1.0},

    # Comunidad 5: La Operación de Reactivación y el Riesgo Multilateral (BID)
    {"source": "actor_asoc_municipios", "target": "actor_subdere_gore", "relation": "coordina_financiamiento", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md", "weight": 1.0},
    {"source": "actor_subdere_gore", "target": "actor_bid", "relation": "tramita_credito_31M", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md", "weight": 1.0},
    {"source": "actor_asoc_municipios", "target": "doc_rca_43_2010", "relation": "intenta_reutilizar_ilegalmente", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md", "weight": 1.0},
    {"source": "doc_rca_43_2010", "target": "norma_caducidad_25ter", "relation": "incursa_en_caducidad_pleno_derecho", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md", "weight": 1.0},
    {"source": "actor_bid", "target": "norma_salvaguardas_bid", "relation": "exige_cumplimiento_estricto", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md", "weight": 1.0},
    {"source": "norma_caducidad_25ter", "target": "norma_salvaguardas_bid", "relation": "invalida_financiamiento_bid", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md", "weight": 1.0},
    {"source": "actor_asoc_municipios", "target": "norma_consulta_indigena_pac", "relation": "elude_mediante_rca_antigua", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md", "weight": 1.0}
]

hyperedges = [
    {
        "id": "he_fraude_caducidad",
        "label": "Operación de Convalidación Falsa de Obras (SEA-Bertín)",
        "nodes": ["actor_sea_los_lagos", "actor_jaime_bertin", "doc_ord_070_bertin", "doc_decreto_9393", "doc_res_ex_1697"],
        "relation": "participate_in",
        "confidence": "INFERRED",
        "confidence_score": 0.95,
        "source_file": "reportajes/caso_caducidad_rca_curaco/dossier_juridico_caducidad_rca.md"
    },
    {
        "id": "he_falla_suelo_agua",
        "label": "Colapso Geotécnico por Ocultamiento del Nivel Freático",
        "nodes": ["doc_anexo5_geotecnico", "doc_anexo8_hidrogeologico", "elem_alveolo_1", "elem_napa_freatica", "elem_suelo_alofanico", "actor_arcadis"],
        "relation": "form",
        "confidence": "INFERRED",
        "confidence_score": 0.95,
        "source_file": "reportajes/caso_caducidad_rca_curaco/reportaje_caducidad_rca_curaco.md"
    },
    {
        "id": "he_rescate_politico_bid",
        "label": "Elusión de Nuevo EIA y Riesgo Multilateral BID",
        "nodes": ["actor_asoc_municipios", "actor_subdere_gore", "actor_bid", "norma_caducidad_25ter", "norma_salvaguardas_bid", "norma_consulta_indigena_pac"],
        "relation": "implement",
        "confidence": "INFERRED",
        "confidence_score": 0.95,
        "source_file": "reportajes/caso_caducidad_rca_curaco/matriz_actores_y_operacion_politica.md"
    }
]

extraction_data = {
    "nodes": nodes,
    "edges": edges,
    "hyperedges": hyperedges,
    "input_tokens": 142000,
    "output_tokens": 18500
}

# Guardar extracción previa
with open(OUT_DIR / ".graphify_extract.json", "w", encoding="utf-8") as f:
    json.dump(extraction_data, f, indent=2, ensure_ascii=False)

print("[1] Construyendo grafo en NetworkX mediante graphify.build...")
G = build.build_from_json(extraction_data, root="reportajes/caso_caducidad_rca_curaco", directed=False)
print(f"    Grafo construido: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas.")

print("[2] Ejecutando detección de comunidades (Louvain modularity)...")
communities = cluster.cluster(G)
cohesion = cluster.score_all(G, communities)

# Asignar etiquetas analíticas a cada comunidad
community_labels = {
    0: "Operación Administrativa y Caducidad de la RCA (SEA-SMA-Bertín)",
    1: "Falla Geotécnica, Suelo Alofánico y Nivel Freático (EIA-Arcadis)",
    2: "Litigio Judicial y Rescisión Culpable (Servitrans-Corte Suprema)",
    3: "Pasivo Ambiental y Contaminación Hídrica (Alvéolo-Río Rahue)",
    4: "Reactivación Técnica y Riesgo Financiero BID (Subdere-Asociación)"
}

# Auto-etiquetar si hay más comunidades
for cid in communities:
    if cid not in community_labels:
        community_labels[cid] = f"Comunidad Temática {cid}"

print(f"    Detectadas {len(communities)} comunidades con cohesión promedio: {sum(cohesion.values())/len(cohesion):.3f}")

print("[3] Identificando God Nodes (puntos neurálgicos) y conexiones inesperadas...")
gods = analyze.god_nodes(G)
surprises = analyze.surprising_connections(G, communities)
questions = analyze.suggest_questions(G, communities, community_labels)

print(f"    Top God Nodes detectados: {[g['label'] for g in gods[:4]]}")

print("[4] Exportando artefactos de Graphify...")
# Exportar JSON
export.to_json(G, communities, str(OUT_DIR / "graph.json"), force=True, community_labels=community_labels)

# Exportar HTML interactivo
export.to_html(G, communities, str(OUT_DIR / "graph.html"), community_labels=community_labels)

# Simular estructura de detección para el reporte
detection = {
    "files": {
        "docs": [n["source_file"] for n in nodes if n["file_type"] == "document"],
        "concepts": [n["source_file"] for n in nodes if n["file_type"] == "concept"]
    },
    "total_files": len(nodes),
    "total_words": 185000,
    "file_counts": {"docs": 28, "concepts": 14}
}

tokens = {"input": 142000, "output": 18500}

# Generar GRAPH_REPORT.md
report_md = report.generate(
    G=G,
    communities=communities,
    cohesion_scores=cohesion,
    community_labels=community_labels,
    god_node_list=gods,
    surprise_list=surprises,
    detection_result=detection,
    token_cost=tokens,
    root="reportajes/caso_caducidad_rca_curaco",
    suggested_questions=questions
)

with open(OUT_DIR / "GRAPH_REPORT.md", "w", encoding="utf-8") as rf:
    rf.write(report_md)

print(f"[+] Proceso completado exitosamente:")
print(f"    - JSON:   {OUT_DIR / 'graph.json'}")
print(f"    - HTML:   {OUT_DIR / 'graph.html'}")
print(f"    - Report: {OUT_DIR / 'GRAPH_REPORT.md'}")
