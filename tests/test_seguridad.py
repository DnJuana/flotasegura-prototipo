"""Pruebas de Seguridad y Control de Acceso (RBAC / OWASP).

Responsable: Integrante F (Bryan Martinez).
Casos de prueba: CP-22 a CP-26.

Correccion de integracion (Felipe Aravena, 13-10-2026): se quitaron las marcas
de conflicto con que se subio el archivo y se ajustaron los nombres a los del
proyecto (fixture `client`; ids fijos del seed en vez de `datos[...]`).
Datos del seed: usuario 2 = conductor1 (camion 1); camion 2 es de conductor2.
"""

import pytest
from app.auth import crear_token
from app.db import get_db


def test_cp22_kilometraje_sin_autorizacion(client, datos):
    """CP-22: Intentar registrar kilometraje sin cabecera Authorization debe devolver 401."""
    camion_id = 1
    payload = {"kilometraje": 12000}

    respuesta = client.post(f"/camiones/{camion_id}/kilometraje", json=payload)

    assert respuesta.status_code == 401
    assert "error" in respuesta.get_json()


def test_cp23_conductor_no_autorizado_registra_kilometraje(client, datos, app):
    """CP-23: Conductor1 intenta registrar kilometraje en camión 2.

    Debe devolver 403 Forbidden y no insertar registros en la BD.
    """
    camion2_id = 2
    conductor1_id = 2

    token = crear_token(conductor1_id, "conductor")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"kilometraje": 25000}

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM registros_kilometraje WHERE camion_id = ?", (camion2_id,))
        conteo_inicial = cursor.fetchone()[0]

    respuesta = client.post(f"/camiones/{camion2_id}/kilometraje", json=payload, headers=headers)

    assert respuesta.status_code == 403
    assert "error" in respuesta.get_json()

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM registros_kilometraje WHERE camion_id = ?", (camion2_id,))
        conteo_final = cursor.fetchone()[0]

    assert conteo_final == conteo_inicial


def test_cp24_conductor_no_autorizado_consulta_estado(client, datos):
    """CP-24: Conductor1 intenta consultar el estado del camión 2.

    Debe devolver 403 Forbidden.
    """
    camion2_id = 2
    conductor1_id = 2

    token = crear_token(conductor1_id, "conductor")
    headers = {"Authorization": f"Bearer {token}"}

    respuesta = client.get(f"/camiones/{camion2_id}/estado", headers=headers)

    assert respuesta.status_code == 403
    assert "error" in respuesta.get_json()


def test_cp25_login_sqli_inyectado(client):
    """CP-25: Intento de SQL Injection en el login (' OR '1'='1).

    Debe responder 401 Unauthorized y no 500.
    """
    payload = {
        "usuario": "' OR '1'='1",
        "contrasena": "password_cualquiera"
    }

    respuesta = client.post("/login", json=payload)

    assert respuesta.status_code == 401
    assert "error" in respuesta.get_json()


def test_cp26_token_tampered_y_vencido(client, datos, app):
    """CP-26: Token manipulado en el medio o expirado debe responder 401."""
    camion1_id = 1
    conductor1_id = 2

    # 1. Token manipulado (alterar carácter en el medio)
    token_valido = crear_token(conductor1_id, "conductor")
    posicion_medio = len(token_valido) // 2
    caracter_original = token_valido[posicion_medio]
    nuevo_caracter = "X" if caracter_original != "X" else "Y"
    token_tampered = token_valido[:posicion_medio] + nuevo_caracter + token_valido[posicion_medio + 1:]

    headers_tampered = {"Authorization": f"Bearer {token_tampered}"}
    respuesta_tampered = client.get(f"/camiones/{camion1_id}/estado", headers=headers_tampered)

    assert respuesta_tampered.status_code == 401

    # 2. Token vencido
    app.config["TOKEN_DURACION_SEG"] = -1
    token_expirado = crear_token(conductor1_id, "conductor")
    headers_expirado = {"Authorization": f"Bearer {token_expirado}"}

    respuesta_expirado = client.get(f"/camiones/{camion1_id}/estado", headers=headers_expirado)

    assert respuesta_expirado.status_code == 401
