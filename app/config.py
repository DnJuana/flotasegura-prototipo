"""Configuracion de la aplicacion."""
import os


class Config:
    # Clave con la que se firman los tokens de sesion.
    # Se lee de una variable de entorno; el valor por defecto es solo para desarrollo.
    SECRET_KEY = os.environ.get("FLOTASEGURA_SECRET_KEY", "clave-solo-para-desarrollo")

    # Ruta del archivo SQLite.
    DATABASE = os.environ.get("FLOTASEGURA_DB", "flotasegura.db")

    # Duracion del token de sesion, en segundos.
    TOKEN_DURACION_SEG = 60 * 60
