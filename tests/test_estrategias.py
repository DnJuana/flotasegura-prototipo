"""Pruebas del patron Strategy (RF3).

Responsable: Integrante A.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
Quitar el pytest.skip al implementarla.
"""
import pytest

PENDIENTE = "pendiente de implementar"


def test_cp_01_km_lejos_del_umbral():
    """CP-01 | Funcional | RF3

    Entrada: plan cada 10.000 km, faltan 5.000. Esperado: estado operativo y km_restantes = 5000.
    """
    pytest.skip(PENDIENTE)


def test_cp_02_km_justo_en_el_umbral():
    """CP-02 | Funcional - caso limite | RF3

    Entrada: km_restantes igual al umbral de aviso. Esperado: alerta_temprana.
    """
    pytest.skip(PENDIENTE)


def test_cp_03_km_sobrepasado():
    """CP-03 | Funcional | RF3

    Entrada: km_actual supera el limite del plan. Esperado: mantencion_vencida y km_restantes <= 0.
    """
    pytest.skip(PENDIENTE)


def test_cp_04_fecha_vencida():
    """CP-04 | Funcional | RF3

    Entrada: plan por fecha con la fecha limite ya pasada. Esperado: mantencion_vencida.
    """
    pytest.skip(PENDIENTE)


def test_cp_05_tipo_de_calculo_desconocido():
    """CP-05 | Funcional - caso de error | RF3

    Entrada: obtener_estrategia('ruta'). Esperado: ValueError.
    """
    pytest.skip(PENDIENTE)
