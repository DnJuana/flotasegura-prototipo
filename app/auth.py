"""Servicio de Autenticacion: inicio de sesion (RF9).

Responsable: Integrante C.

Incluye el hash de contrasenas, la emision y lectura del token de sesion
y el endpoint POST /login.
"""
from flask import Blueprint, jsonify

bp = Blueprint("auth", __name__)


def hash_contrasena(contrasena: str) -> str:
    """Devuelve el hash de la contrasena para guardarlo en la base.

    TODO (C): usar werkzeug.security.generate_password_hash.
    Nunca se guarda la contrasena en texto plano (RNF de seguridad).
    """
    raise NotImplementedError("hash_contrasena pendiente")


def verificar_contrasena(hash_guardado: str, contrasena: str) -> bool:
    """TODO (C): usar werkzeug.security.check_password_hash."""
    raise NotImplementedError("verificar_contrasena pendiente")


def crear_token(usuario_id: int, rol: str) -> str:
    """Crea el token firmado que el cliente envia en cada peticion.

    TODO (C): usar itsdangerous.URLSafeTimedSerializer con
    current_app.config["SECRET_KEY"]. El token lleva usuario_id y rol.
    """
    raise NotImplementedError("crear_token pendiente")


def leer_token(token: str):
    """Devuelve {"usuario_id": ..., "rol": ...} o None si el token es
    invalido, fue alterado o ya expiro (TOKEN_DURACION_SEG).

    TODO (C).
    """
    raise NotImplementedError("leer_token pendiente")


@bp.post("/login")
def login():
    """POST /login  -  cuerpo JSON: {"usuario": "...", "contrasena": "..."}

    Respuestas esperadas:
      200 {"token": "...", "rol": "..."}
      400 si falta algun campo
      401 si las credenciales no son validas (mismo mensaje para usuario
          inexistente y para contrasena incorrecta)

    TODO (C).
    """
    return jsonify(error="login pendiente de implementar"), 501
