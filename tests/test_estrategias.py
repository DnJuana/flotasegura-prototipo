"""Pruebas del patron Strategy (RF3).

Responsable: Integrante A.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
"""
from datetime import date

import pytest

from app.estrategias import (
    ALERTA_TEMPRANA,
    MANTENCION_VENCIDA,
    OPERATIVO,
    CalculoPorFecha,
    CalculoPorKm,
    obtener_estrategia,
)

HOY = date(2026, 10, 11)


def plan_km(**cambios):
    plan = {
        "id": 1, "camion_id": 1, "tipo": "aceite", "tipo_calculo": "km",
        "intervalo_km": 10000, "km_ultima_mantencion": 0, "umbral_aviso_km": 1000,
        "intervalo_dias": None, "fecha_ultima_mantencion": None, "umbral_aviso_dias": None,
    }
    plan.update(cambios)
    return plan


def plan_fecha(**cambios):
    plan = {
        "id": 2, "camion_id": 1, "tipo": "frenos", "tipo_calculo": "fecha",
        "intervalo_km": None, "km_ultima_mantencion": None, "umbral_aviso_km": None,
        "intervalo_dias": 180, "fecha_ultima_mantencion": "2026-06-01", "umbral_aviso_dias": 15,
    }
    plan.update(cambios)
    return plan


def test_cp_01_km_lejos_del_umbral():
    """CP-01 | Funcional | RF3

    Entrada: plan cada 10.000 km, faltan 5.000. Esperado: estado operativo y km_restantes = 5000.
    """
    r = CalculoPorKm().calcular(plan_km(), 5000, HOY)
    assert r.km_restantes == 5000
    assert r.estado == OPERATIVO
    assert r.dias_restantes is None and r.fecha_estimada is None


def test_cp_02_km_justo_en_el_umbral():
    """CP-02 | Funcional - caso limite | RF3

    Entrada: km_restantes igual al umbral de aviso. Esperado: alerta_temprana.
    """
    r = CalculoPorKm().calcular(plan_km(), 9000, HOY)
    assert r.km_restantes == 1000
    assert r.estado == ALERTA_TEMPRANA


def test_cp_03_km_sobrepasado():
    """CP-03 | Funcional | RF3

    Entrada: km_actual supera el limite del plan. Esperado: mantencion_vencida y km_restantes <= 0.
    """
    r = CalculoPorKm().calcular(plan_km(), 10500, HOY)
    assert r.km_restantes <= 0
    assert r.estado == MANTENCION_VENCIDA


def test_cp_04_fecha_vencida():
    """CP-04 | Funcional | RF3

    Entrada: plan por fecha con la fecha limite ya pasada. Esperado: mantencion_vencida.
    """
    plan = plan_fecha(fecha_ultima_mantencion="2026-01-01")  # vencio el 2026-06-30
    r = CalculoPorFecha().calcular(plan, 0, HOY)
    assert r.fecha_estimada == date(2026, 6, 30)
    assert r.dias_restantes < 0
    assert r.estado == MANTENCION_VENCIDA
    assert r.km_restantes is None


def test_cp_05_tipo_de_calculo_desconocido():
    """CP-05 | Funcional - caso de error | RF3

    Entrada: obtener_estrategia('ruta'). Esperado: ValueError.
    """
    with pytest.raises(ValueError):
        obtener_estrategia("ruta")


# Pruebas adicionales (no estan en el plan: agregar al plan si se quieren citar)
def test_obtener_estrategia_devuelve_la_clase_correcta():
    assert isinstance(obtener_estrategia("km"), CalculoPorKm)
    assert isinstance(obtener_estrategia("fecha"), CalculoPorFecha)


def test_fecha_en_el_umbral_y_fuera_de_el():
    # fecha_estimada = 2026-12-01 -> faltan 51 dias desde HOY
    plan = plan_fecha(fecha_ultima_mantencion="2026-06-04", umbral_aviso_dias=51)
    assert CalculoPorFecha().calcular(plan, 0, HOY).estado == ALERTA_TEMPRANA
    plan["umbral_aviso_dias"] = 50
    assert CalculoPorFecha().calcular(plan, 0, HOY).estado == OPERATIVO


def test_plan_con_campos_faltantes_lanza_valueerror():
    with pytest.raises(ValueError):
        CalculoPorKm().calcular(plan_km(intervalo_km=None), 0, HOY)
