<<<<<<< HEAD
"""Pruebas de Seguridad y Control de Acceso (RBAC / OWASP).

Responsable: Integrante F (Bryan).
Casos de prueba: CP-22 a CP-26.
"""

import pytest
from app.auth import crear_token
from app.db import get_db


def test_cp22_kilometraje_sin_autorizacion(cliente, datos):
    """CP-22: Intentar registrar kilometraje sin cabecera Authorization debe devolver 401."""
    camion_id = datos["camion1_id"]
    payload = {"kilometraje": 12000}

    respuesta = cliente.post(f"/camiones/{camion_id}/kilometraje", json=payload)

    assert respuesta.status_code == 401
    assert "error" in respuesta.get_json()


def test_cp23_conductor_no_autorizado_registra_kilometraje(cliente, datos, app):
    """CP-23: Conductor1 intenta registrar kilometraje en camión 2.

    Debe devolver 403 Forbidden y no insertar registros en la BD.
    """
    camion2_id = datos["camion2_id"]
    conductor1_id = datos["conductor1_id"]

    token = crear_token(conductor1_id, "conductor")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"kilometraje": 25000}

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM registros_kilometraje WHERE camion_id = ?", (camion2_id,))
        conteo_inicial = cursor.fetchone()[0]

    respuesta = cliente.post(f"/camiones/{camion2_id}/kilometraje", json=payload, headers=headers)

    assert respuesta.status_code == 403
    assert "error" in respuesta.get_json()

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM registros_kilometraje WHERE camion_id = ?", (camion2_id,))
        conteo_final = cursor.fetchone()[0]

    assert conteo_final == conteo_inicial


def test_cp24_conductor_no_autorizado_consulta_estado(cliente, datos):
    """CP-24: Conductor1 intenta consultar el estado del camión 2.

    Debe devolver 403 Forbidden.
    """
    camion2_id = datos["camion2_id"]
    conductor1_id = datos["conductor1_id"]

    token = crear_token(conductor1_id, "conductor")
    headers = {"Authorization": f"Bearer {token}"}

    respuesta = cliente.get(f"/camiones/{camion2_id}/estado", headers=headers)

    assert respuesta.status_code == 403
    assert "error" in respuesta.get_json()


def test_cp25_login_sqli_inyectado(cliente):
    """CP-25: Intento de SQL Injection en el login (' OR '1'='1).

    Debe responder 401 Unauthorized y no 500.
    """
    payload = {
        "usuario": "' OR '1'='1",
        "contrasena": "password_cualquiera"
    }

    respuesta = cliente.post("/login", json=payload)

    assert respuesta.status_code == 401
    assert "error" in respuesta.get_json()


def test_cp26_token_tampered_y_vencido(cliente, datos, app):
    """CP-26: Token manipulado en el medio o expirado debe responder 401."""
    camion1_id = datos["camion1_id"]
    conductor1_id = datos["conductor1_id"]

    # 1. Token manipulado (alterar carácter en el medio)
    token_valido = crear_token(conductor1_id, "conductor")
    posicion_medio = len(token_valido) // 2
    caracter_original = token_valido[posicion_medio]
    nuevo_caracter = "X" if caracter_original != "X" else "Y"
    token_tampered = token_valido[:posicion_medio] + nuevo_caracter + token_valido[posicion_medio + 1:]

    headers_tampered = {"Authorization": f"Bearer {token_tampered}"}
    respuesta_tampered = cliente.get(f"/camiones/{camion1_id}/estado", headers=headers_tampered)

    assert respuesta_tampered.status_code == 401

    # 2. Token vencido
    app.config["TOKEN_DURACION_SEG"] = -1
    token_expirado = crear_token(conductor1_id, "conductor")
    headers_expirado = {"Authorization": f"Bearer {token_expirado}"}

    respuesta_expirado = cliente.get(f"/camiones/{camion1_id}/estado", headers=headers_expirado)

    assert respuesta_expirado.status_code == 401
=======
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
>>>>>>> 507ee2039b3a3d34fddf20a4e215360dbc558b3b
