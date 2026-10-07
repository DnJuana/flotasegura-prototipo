"""Configuracion comun de las pruebas. Archivo base: ya esta listo.

Cada prueba recibe una aplicacion con una base de datos SQLite nueva y
vacia (solo las tablas), creada en una carpeta temporal.
"""
import pytest

from app import create_app
from app.db import get_db, init_db


@pytest.fixture
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "pruebas.db"),
        "SECRET_KEY": "clave-de-pruebas",
    })
    with app.app_context():
        init_db()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def conexion(app):
    return get_db()


# TODO (E): cuando seed.cargar_datos() este listo, agregar aqui un fixture
# "datos" que lo ejecute, para que las pruebas partan con usuarios y camiones.
