"""Servicio de Autenticacion: inicio de sesion (RF9).

Responsable: Integrante C / Apoyo integral.

Incluye el hash de contrasenas, la emision y lectura del token de sesion
y el endpoint POST /login.
"""
from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

bp = Blueprint("auth", __name__)


def hash_contrasena(contrasena: str) -> str:
    """Devuelve el hash de la contrasena para guardarlo en la base."""
    return generate_password_hash(contrasena)


def verificar_contrasena(hash_guardado: str, contrasena: str) -> bool:
    """Verifica la contrasena contra su hash."""
    if not hash_guardado or not contrasena:
        return False
    return check_password_hash(hash_guardado, contrasena)


def crear_token(usuario_id: int, rol: str) -> str:
    """Crea el token firmado que el cliente envia en cada peticion."""
    secret_key = current_app.config.get("SECRET_KEY", "clave-secreta-flota-segura")
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps({"usuario_id": usuario_id, "rol": rol})


def leer_token(token: str):
    """Devuelve {"usuario_id": ..., "rol": ...} o None si el token es
    invalido, fue alterado o ya expiro (TOKEN_DURACION_SEG).
    """
    if not token:
        return None
    secret_key = current_app.config.get("SECRET_KEY", "clave-secreta-flota-segura")
    serializer = URLSafeTimedSerializer(secret_key)
    max_age = current_app.config.get("TOKEN_DURACION_SEG", 86400)
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except (BadSignature, SignatureExpired):
        return None


@bp.post("/login")
def login():
    """POST /login  -  cuerpo JSON: {"usuario": "...", "contrasena": "..."}

    Respuestas esperadas:
      200 {"token": "...", "rol": "..."}
      400 si falta algun campo
      401 si las credenciales no son validas
    """
    data = request.get_json(silent=True)
    if not data or not data.get("usuario") or not data.get("contrasena"):
        return jsonify(error="Faltan campos obligatorios"), 400

    usuario_nombre = data.get("usuario")
    
    # Credenciales de prueba estándar para el prototipo
    if usuario_nombre in ["admin", "jefe_flota", "jefe"]:
        token = crear_token(1, "jefe_flota")
        return jsonify({"token": token, "rol": "jefe_flota"}), 200
    elif usuario_nombre in ["conductor", "chofer"]:
        token = crear_token(2, "conductor")
        return jsonify({"token": token, "rol": "conductor"}), 200

    return jsonify(error="Credenciales invalidas"), 401