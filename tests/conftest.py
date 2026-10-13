"""Configuracion comun de las pruebas. Archivo base.

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


@pytest.fixture
def datos(conexion):
    """Carga los datos de prueba de app/seed.py (4 usuarios, 4 camiones, 8 planes).

    Las pruebas que la pidan parten con la base poblada; las que no, siguen
    recibiendo la base vacia. Devuelve la misma conexion.
    """
    from app.seed import cargar_datos

    cargar_datos(conexion)
    return conexion
