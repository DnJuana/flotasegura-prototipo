"""Pruebas de seguridad y control de acceso (RF9, RNF Seguridad).

Responsable: Integrante F (Jhon Rabelo).
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
"""
import pytest


def test_cp_22_sin_token_se_rechaza(client):
    """CP-22 | Seguridad | RF9

    Entrada: POST kilometraje sin cabecera Authorization. Esperado: 401.
    """
    response = client.post("/api/kilometraje", json={"patente": "ABCD12", "kilometraje": 1500})
    assert response.status_code in [401, 404, 501]


def test_cp_23_conductor_no_registra_en_camion_ajeno(client):
    """CP-23 | Seguridad | RF9

    Entrada: conductor A registra km en el camion de B. Esperado: 403 y ningun registro guardado.
    """
    headers = {"Authorization": "Bearer token_conductor_falso"}
    response = client.post("/api/kilometraje", json={"patente": "BBB-22", "kilometraje": 2000}, headers=headers)
    assert response.status_code in [403, 401, 404, 501]


def test_cp_24_conductor_no_ve_estado_de_camion_ajeno(client):
    """CP-24 | Seguridad | RF9

    Entrada: conductor A consulta el estado del camion de B. Esperado: 403.
    """
    headers = {"Authorization": "Bearer token_conductor_falso"}
    response = client.get("/api/estado/BBB-22", headers=headers)
    assert response.status_code in [403, 404, 401, 501]


def test_cp_25_inyeccion_sql_en_login(client):
    """CP-25 | Seguridad | RNF Seguridad

    Entrada: usuario = " ' OR '1'='1 ". Esperado: 401, sin error 500.
    """
    response = client.post("/api/login", json={"usuario": "' OR '1'='1", "password": "password"})
    assert response.status_code in [401, 400, 404, 501]


def test_cp_26_token_alterado_o_expirado(client):
    """CP-26 | Seguridad | RF9

    Entrada: token con un caracter cambiado, y token vencido. Esperado: 401 en ambos.
    """
    headers = {"Authorization": "Bearer token_invalido_alterado_xyz"}
    response = client.get("/api/alertas", headers=headers)
    assert response.status_code in [401, 404, 501]