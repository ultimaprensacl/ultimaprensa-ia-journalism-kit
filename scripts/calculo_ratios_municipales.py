#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Última Prensa - Auditoría Rápida de Indicadores y Ratios Municipales
====================================================================
Calcula ratios de solvencia, liquidez corriente, impacto per cápita
y equivalencias de inversión comunitaria a partir de balances de CGR.

Uso:
    python scripts/calculo_ratios_municipales.py
"""

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

def mostrar_diagnostico_financiero(nombre_comuna: str, poblacion: int, caja: float, pasivos: float, deudas_prescritas: float, desfalco_total: float):
    ratio = calcular_liquidez(caja, pasivos)
    per_capita_prescrito = calcular_impacto_per_capita(deudas_prescritas, poblacion)
    per_capita_total = calcular_impacto_per_capita(desfalco_total, poblacion)

    print("=" * 70)
    print(f"  DIAGNÓSTICO PERICIAL FINANCIERO: MUNICIPALIDAD DE {nombre_comuna.upper()}")
    print("=" * 70)
    print(f"Población comunal: {poblacion:,} habitantes\n")
    print(f"1. ÍNDICE DE LIQUIDEZ CORRIENTE:")
    print(f"   - Disponibilidades en Caja (CGR): ${caja:,.0f}")
    print(f"   - Pasivos a Corto Plazo:          ${pasivos:,.0f}")
    print(f"   -> RATIO RESULTANTE:              {ratio:.2f}")
    if ratio < 1.0:
        print(f"   [!] ESTADO: INSOLVENCIA TÉCNICA (Menos de $1 disponible por cada $1 adeudado)")
    else:
        print(f"   [+] ESTADO: SOLVENTE")
    
    print(f"\n2. IMPACTO CIUDADANO PER CÁPITA:")
    print(f"   - Pérdida por deudas morosas prescritas: ${deudas_prescritas:,.0f}")
    print(f"   -> Costo por habitante:                  ${per_capita_prescrito:,.0f} por vecino")
    print(f"   -> Costo por familia (4 personas):       ${per_capita_prescrito * 4:,.0f}")
    print(f"   - Descalabro patrimonial total:          ${desfalco_total:,.0f}")
    print(f"   -> Impacto patrimonial por vecino:       ${per_capita_total:,.0f}")

    print("\n3. EQUIVALENCIAS COMUNITARIAS ESTIMADAS:")
    print(f"   - Postas de Salud Rural (~$550M c/u):    {deudas_prescritas / 550_000_000:.1f} postas nuevas")
    print(f"   - Ambulancias avanzadas (~$90M c/u):     {deudas_prescritas / 90_000_000:.1f} ambulancias")
    print(f"   - Pavimentación urbana (~$350M/km):      {deudas_prescritas / 350_000_000:.1f} kilómetros lineales")
    print(f"   - Camiones recolectores (~$165M c/u):    {desfalco_total / 165_000_000:.1f} camiones")
    print("=" * 70)

if __name__ == "__main__":
    # Ejemplo con parámetros de Llanquihue
    mostrar_diagnostico_financiero(
        nombre_comuna="Llanquihue",
        poblacion=18500,
        caja=2399000000,
        pasivos=4201000000,
        deudas_prescritas=3405122295,
        desfalco_total=11072750168
    )
