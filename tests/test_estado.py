"""Pruebas de consulta de estado y alertas (RF4).

Responsable: Integrante E.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
Quitar el pytest.skip al implementarla.
"""
import pytest

PENDIENTE = "pendiente de implementar"


def test_cp_20_estado_devuelve_color_del_semaforo():
    """CP-20 | Funcional | RF4

    Entrada: GET estado de un camion en alerta temprana. Esperado: 200 con color amarillo.
    """
    pytest.skip(PENDIENTE)


def test_cp_21_cada_usuario_ve_solo_sus_alertas():
    """CP-21 | Seguridad | RF9

    Entrada: GET /alertas como conductor. Esperado: solo alertas con su destinatario_id.
    """
    pytest.skip(PENDIENTE)
