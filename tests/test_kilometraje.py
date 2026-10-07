"""Pruebas del registro de kilometraje (RF1).

Responsable: Integrante D.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
Quitar el pytest.skip al implementarla.
"""
import pytest

PENDIENTE = "pendiente de implementar"


def test_cp_14_registro_valido():
    """CP-14 | Funcional | RF1

    Entrada: conductor registra un km mayor al actual en su camion. Esperado: 201 y km_actual actualizado.
    """
    pytest.skip(PENDIENTE)


def test_cp_15_km_menor_al_actual():
    """CP-15 | Funcional - caso de error | RF1

    Entrada: km inferior al ultimo registrado. Esperado: 400 y km_actual sin cambios.
    """
    pytest.skip(PENDIENTE)


def test_cp_16_km_igual_al_actual():
    """CP-16 | Funcional - caso limite | RF1

    Entrada: km identico al actual. Esperado: definir y documentar la regla (aceptar o rechazar).
    """
    pytest.skip(PENDIENTE)


def test_cp_17_km_negativo_o_no_numerico():
    """CP-17 | Funcional - caso de error | RF1

    Entrada: -5, 'abc', 1500.5, null. Esperado: 400 en todos los casos.
    """
    pytest.skip(PENDIENTE)


def test_cp_18_camion_inexistente():
    """CP-18 | Funcional - caso de error | RF1

    Entrada: id de camion que no existe. Esperado: 404.
    """
    pytest.skip(PENDIENTE)


def test_cp_19_registro_que_cruza_el_umbral_genera_alerta():
    """CP-19 | Funcional - flujo completo | RF1, RF3, RF4

    Entrada: km que deja al camion dentro del umbral. Esperado: estado alerta_temprana y alertas creadas.
    """
    pytest.skip(PENDIENTE)
