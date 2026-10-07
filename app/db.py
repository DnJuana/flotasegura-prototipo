"""Conexion a SQLite. Archivo base: ya esta listo, no requiere cambios."""
import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    """Devuelve la conexion de la peticion actual (una por peticion)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def cerrar_db(_error=None):
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def init_db():
    """Crea las tablas definidas en schema.sql si no existen."""
    esquema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    conexion = get_db()
    conexion.executescript(esquema)
    conexion.commit()


def registrar(app):
    app.teardown_appcontext(cerrar_db)
