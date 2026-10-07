"""Pruebas del patron Observer (RF4).

Responsable: Integrante B.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
Quitar el pytest.skip al implementarla.
"""
import pytest

PENDIENTE = "pendiente de implementar"


def test_cp_06_al_cruzar_umbral_se_alerta_a_jefe_y_conductor():
    """CP-06 | Funcional | RF4

    Entrada: notificar() con los dos notificadores suscritos. Esperado: una alerta para el jefe de flota y otra para el conductor.
    """
    pytest.skip(PENDIENTE)


def test_cp_07_camion_sin_conductor_solo_alerta_al_jefe():
    """CP-07 | Funcional - caso limite | RF4

    Entrada: camion con conductor_id nulo. Esperado: solo se crea la alerta del jefe de flota, sin error.
    """
    pytest.skip(PENDIENTE)


def test_cp_08_observador_desuscrito_no_recibe_alerta():
    """CP-08 | Funcional | RF4

    Entrada: suscribir, desuscribir y notificar. Esperado: cero alertas para ese observador.
    """
    pytest.skip(PENDIENTE)


def test_cp_09_peor_estado_entre_varios_planes():
    """CP-09 | Funcional | RF4

    Entrada: un plan operativo y otro vencido. Esperado: mantencion_vencida.
    """
    pytest.skip(PENDIENTE)
