"""Pruebas del inicio de sesion (RF9).

Responsable: Integrante C.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
Quitar el pytest.skip al implementarla.
"""
import pytest

PENDIENTE = "pendiente de implementar"




def test_cp_10_login_correcto_entrega_token():
    """CP-10 | Funcional | RF9: login correcto con token y rol."""

    from pathlib import Path
    from tempfile import TemporaryDirectory

    from app import create_app
    from app.auth import leer_token
    from app.db import get_db, init_db
    from app.seed import cargar_datos

    with TemporaryDirectory() as carpeta:
        ruta_db = str(Path(carpeta) / "flotasegura_test.db")

        app = create_app({
            "TESTING": True,
            "DATABASE": ruta_db,
            "SECRET_KEY": "clave-exclusiva-para-testing",
            "TOKEN_DURACION_SEG": 3600,
        })

        with app.app_context():
            init_db()
            cargar_datos(get_db())

            cliente = app.test_client()

            respuesta = cliente.post(
                "/login",
                json={
                    "usuario": "jefe.flota",
                    "contrasena": "FlotaSegura.2026"
                }
            )

            assert respuesta.status_code == 200

            datos = respuesta.get_json()

            assert isinstance(datos.get("token"), str)
            assert datos["rol"] == "jefe_flota"

            token_decodificado = leer_token(datos["token"])

            assert token_decodificado is not None
            assert token_decodificado["usuario_id"] == 1
            assert token_decodificado["rol"] == "jefe_flota"



def test_cp_11_contrasena_incorrecta():
    """CP-11 | Seguridad | RF9: rechaza contraseña incorrecta."""

    from pathlib import Path
    from tempfile import TemporaryDirectory

    from app import create_app
    from app.db import get_db, init_db
    from app.seed import cargar_datos

    with TemporaryDirectory() as carpeta:
        ruta_db = str(Path(carpeta) / "flotasegura_test.db")

        app = create_app({
            "TESTING": True,
            "DATABASE": ruta_db,
            "SECRET_KEY": "clave-exclusiva-para-testing",
            "TOKEN_DURACION_SEG": 3600,
        })

        with app.app_context():
            init_db()
            cargar_datos(get_db())

            cliente = app.test_client()

            respuesta = cliente.post(
                "/login",
                json={
                    "usuario": "jefe.flota",
                    "contrasena": "ClaveIncorrecta123"
                }
            )

            assert respuesta.status_code == 401

            datos = respuesta.get_json()

            assert datos["error"] == "Credenciales inválidas"
            assert "token" not in datos



def test_cp_12_login_sin_campos():
    """CP-12 | Funcional | RF9: rechaza campos faltantes."""

    from app import create_app

    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "clave-exclusiva-para-testing",
    })

    cliente = app.test_client()

    respuesta = cliente.post(
        "/login",
        json={"usuario": "jefe.flota"}
    )

    assert respuesta.status_code == 400

    datos = respuesta.get_json()

    assert datos["error"] == "Usuario y contraseña son obligatorios"
    assert "token" not in datos



def test_cp_13_la_contrasena_se_guarda_con_hash():
    """CP-13 | Seguridad: la contraseña se almacena con hash."""

    from pathlib import Path
    from tempfile import TemporaryDirectory

    from app import create_app
    from app.db import get_db, init_db
    from app.seed import cargar_datos
    from app.auth import verificar_contrasena

    with TemporaryDirectory() as carpeta:
        ruta_db = str(Path(carpeta) / "flotasegura_test.db")

        app = create_app({
            "TESTING": True,
            "DATABASE": ruta_db,
            "SECRET_KEY": "clave-exclusiva-para-testing",
        })

        with app.app_context():
            init_db()
            cargar_datos(get_db())

            usuario = get_db().execute(
                "SELECT hash_contrasena FROM usuarios "
                "WHERE nombre_usuario = ?",
                ("jefe.flota",)
            ).fetchone()

            assert usuario is not None

            hash_guardado = usuario["hash_contrasena"]

            assert isinstance(hash_guardado, str)
            assert hash_guardado != "FlotaSegura.2026"

            assert verificar_contrasena(
                hash_guardado, "FlotaSegura.2026"
            ) is True

            assert verificar_contrasena(
                hash_guardado, "ClaveIncorrecta123"
            ) is False
