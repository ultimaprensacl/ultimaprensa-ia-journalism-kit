#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Última Prensa - Auditoría Rápida de Indicadores y Ratios Municipales
====================================================================
Calcula ratios de solvencia, liquidez corriente, impacto per cápita,
peso de personal a honorarios y equivalencias de inversión comunitaria
a partir de balances de CGR e informes de auditoría.

Uso:
    python scripts/calculo_ratios_municipales.py
    python scripts/calculo_ratios_municipales.py --comuna Osorno --poblacion 173000 --caja 4500000000 --pasivos 3200000000
"""

import sys
import argparse


def calcular_liquidez(disponibilidades: float, pasivos_corrientes: float) -> float:
    """Calcula el índice de liquidez corriente (Activo Circulante Disponible / Pasivo Circulante)."""
    if pasivos_corrientes == 0:
        return 0.0
    return disponibilidades / pasivos_corrientes


def calcular_impacto_per_capita(monto_total: float, poblacion: int) -> float:
    """Calcula el costo per cápita de un detrimento o desfalco patrimonial."""
    if poblacion == 0:
        return 0.0
    return monto_total / poblacion


def calcular_ratio_honorarios(gasto_honorarios: float, gasto_total_personal: float) -> float:
    """Calcula el porcentaje de gasto en personal a honorarios sobre el gasto total en personal."""
    if gasto_total_personal == 0:
        return 0.0
    return (gasto_honorarios / gasto_total_personal) * 100.0


def mostrar_diagnostico_financiero(
    nombre_comuna: str,
    poblacion: int,
    caja: float,
    pasivos: float,
    deudas_prescritas: float = 0.0,
    desfalco_total: float = 0.0,
    gasto_honorarios: float = 0.0,
    gasto_total_personal: float = 0.0
):
    ratio = calcular_liquidez(caja, pasivos)
    per_capita_prescrito = calcular_impacto_per_capita(deudas_prescritas, poblacion)
    per_capita_total = calcular_impacto_per_capita(desfalco_total, poblacion)

    print("=" * 70)
    print(f"  DIAGNÓSTICO PERICIAL FINANCIERO: MUNICIPALIDAD DE {nombre_comuna.upper()}")
    print("=" * 70)
    print(f"Población comunal: {poblacion:,} habitantes\n")

    print("1. ÍNDICE DE LIQUIDEZ CORRIENTE:")
    print(f"   - Disponibilidades en Caja (CGR): ${caja:,.0f}")
    print(f"   - Pasivos a Corto Plazo:          ${pasivos:,.0f}")
    print(f"   -> RATIO RESULTANTE:              {ratio:.2f}")
    if ratio < 1.0:
        print("   [!] ESTADO: INSOLVENCIA TÉCNICA (Menos de $1 disponible por cada $1 adeudado)")
    else:
        print("   [+] ESTADO: SOLVENTE")

    if gasto_total_personal > 0:
        ratio_h = calcular_ratio_honorarios(gasto_honorarios, gasto_total_personal)
        print("\n2. PESO DEL PERSONAL A HONORARIOS:")
        print(f"   - Gasto en Honorarios (Subt. 21.03/04): ${gasto_honorarios:,.0f}")
        print(f"   - Gasto Total en Personal (Subt. 21):   ${gasto_total_personal:,.0f}")
        print(f"   -> RATIO HONORARIOS / PERSONAL TOTAL:   {ratio_h:.1f} %")
        if ratio_h > 20.0:
            print("   [!] ALERTA FORENSE: Gasto en honorarios supera el umbral prudencial del 20 %")
        else:
            print("   [+] Cumple con parámetros referenciales ordinarios")

    if deudas_prescritas > 0 or desfalco_total > 0:
        print("\n3. IMPACTO CIUDADANO PER CÁPITA:")
        if deudas_prescritas > 0:
            print(f"   - Pérdida por deudas morosas prescritas: ${deudas_prescritas:,.0f}")
            print(f"   -> Costo por habitante:                  ${per_capita_prescrito:,.0f} por vecino")
            print(f"   -> Costo por familia (4 personas):       ${per_capita_prescrito * 4:,.0f}")
        if desfalco_total > 0:
            print(f"   - Descalabro patrimonial total:          ${desfalco_total:,.0f}")
            print(f"   -> Impacto patrimonial por vecino:       ${per_capita_total:,.0f}")

    if deudas_prescritas > 0 or desfalco_total > 0:
        base_calc = deudas_prescritas if deudas_prescritas > 0 else desfalco_total
        print("\n4. EQUIVALENCIAS COMUNITARIAS ESTIMADAS:")
        print(f"   - Postas de Salud Rural (~$550M c/u):    {base_calc / 550_000_000:.1f} postas nuevas")
        print(f"   - Ambulancias avanzadas (~$90M c/u):     {base_calc / 90_000_000:.1f} ambulancias")
        print(f"   - Pavimentación urbana (~$350M/km):      {base_calc / 350_000_000:.1f} kilómetros lineales")
        print(f"   - Camiones recolectores (~$165M c/u):    {base_calc / 165_000_000:.1f} camiones")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Auditoría Rápida de Indicadores y Ratios Municipales para Última Prensa"
    )
    parser.add_argument("--comuna", type=str, default="Llanquihue", help="Nombre de la comuna auditada")
    parser.add_argument("--poblacion", type=int, default=18500, help="Población comunal estimada")
    parser.add_argument("--caja", type=float, default=2399000000, help="Disponibilidades en caja (CGR)")
    parser.add_argument("--pasivos", type=float, default=4201000000, help="Pasivos a corto plazo")
    parser.add_argument("--deudas-prescritas", type=float, default=3405122295, help="Pérdida por prescripciones")
    parser.add_argument("--desfalco", type=float, default=11072750168, help="Descalabro patrimonial consolidado")
    parser.add_argument("--honorarios", type=float, default=0.0, help="Gasto en personal a honorarios")
    parser.add_argument("--gastos-personal", type=float, default=0.0, help="Gasto total en personal")
    args = parser.parse_args()

    mostrar_diagnostico_financiero(
        nombre_comuna=args.comuna,
        poblacion=args.poblacion,
        caja=args.caja,
        pasivos=args.pasivos,
        deudas_prescritas=args.deudas_prescritas,
        desfalco_total=args.desfalco,
        gasto_honorarios=args.honorarios,
        gasto_total_personal=args.gastos_personal
    )


if __name__ == "__main__":
    main()
