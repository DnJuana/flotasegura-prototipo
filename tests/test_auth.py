"""Pruebas del inicio de sesion (RF9).

Responsable: Integrante C.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
Quitar el pytest.skip al implementarla.
"""
import pytest

PENDIENTE = "pendiente de implementar"


def test_cp_10_login_correcto_entrega_token():
    """CP-10 | Funcional | RF9

    Entrada: usuario y contrasena validos. Esperado: 200 con token y rol.
    """
    pytest.skip(PENDIENTE)


def test_cp_11_contrasena_incorrecta():
    """CP-11 | Seguridad - caso de error | RF9

    Entrada: usuario valido con contrasena erronea. Esperado: 401, mismo mensaje que para usuario inexistente.
    """
    pytest.skip(PENDIENTE)


def test_cp_12_login_sin_campos():
    """CP-12 | Funcional - caso de error | RF9

    Entrada: cuerpo vacio o sin contrasena. Esperado: 400.
    """
    pytest.skip(PENDIENTE)


def test_cp_13_la_contrasena_se_guarda_con_hash():
    """CP-13 | Seguridad | RNF Seguridad

    Entrada: leer hash_contrasena de la base. Esperado: no contiene la contrasena en texto plano.
    """
    pytest.skip(PENDIENTE)
