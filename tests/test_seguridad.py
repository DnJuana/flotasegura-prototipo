"""Pruebas de seguridad y control de acceso (RF9, RNF Seguridad).

Responsable: Integrante F.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
Quitar el pytest.skip al implementarla.
"""
import pytest

PENDIENTE = "pendiente de implementar"


def test_cp_22_sin_token_se_rechaza():
    """CP-22 | Seguridad | RF9

    Entrada: POST kilometraje sin cabecera Authorization. Esperado: 401.
    """
    pytest.skip(PENDIENTE)


def test_cp_23_conductor_no_registra_en_camion_ajeno():
    """CP-23 | Seguridad | RF9

    Entrada: conductor A registra km en el camion de B. Esperado: 403 y ningun registro guardado.
    """
    pytest.skip(PENDIENTE)


def test_cp_24_conductor_no_ve_estado_de_camion_ajeno():
    """CP-24 | Seguridad | RF9

    Entrada: conductor A consulta el estado del camion de B. Esperado: 403.
    """
    pytest.skip(PENDIENTE)


def test_cp_25_inyeccion_sql_en_login():
    """CP-25 | Seguridad | RNF Seguridad

    Entrada: usuario = " ' OR '1'='1 ". Esperado: 401, sin error 500.
    """
    pytest.skip(PENDIENTE)


def test_cp_26_token_alterado_o_expirado():
    """CP-26 | Seguridad | RF9

    Entrada: token con un caracter cambiado, y token vencido. Esperado: 401 en ambos.
    """
    pytest.skip(PENDIENTE)
