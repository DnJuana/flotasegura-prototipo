"""Servicio de Autenticacion: inicio de sesion (RF9)."""
from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

try:
    from app.db import get_db
except ImportError:
    from .db import get_db

bp = Blueprint("auth", __name__)


def hash_contrasena(contrasena: str) -> str:
    return generate_password_hash(contrasena)


def verificar_contrasena(hash_guardado: str, contrasena: str) -> bool:
    return check_password_hash(hash_guardado, contrasena)


def crear_token(usuario_id: int, rol: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"usuario_id": usuario_id, "rol": rol})


def leer_token(token: str):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    duracion = current_app.config.get("TOKEN_DURACION_SEG", 3600)
    try:
        datos = serializer.loads(token, max_age=duracion)
        if isinstance(datos, dict) and "usuario_id" in datos and "rol" in datos:
            return datos
        return None
    except Exception:
        return None


@bp.post("/login")
def login():
    datos = request.get_json(silent=True)
    if not datos or not isinstance(datos, dict):
        return jsonify(error="Cuerpo JSON invalido o ausente"), 400

    usuario = datos.get("usuario")
    contrasena = datos.get("contrasena")

    if not usuario or not contrasena:
        return jsonify(error="Faltan campos requeridos"), 400

    db = get_db()
    cursor = db.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
    user = cursor.fetchone()

    if user is None:
        return jsonify(error="Credenciales invalidas"), 401

    try:
        hash_guardado = user["contrasena"]
        user_id = user["id"]
        rol = user["rol"]
    except (TypeError, KeyError):
        user_id = user[0]
        hash_guardado = user[2]
        rol = user[3]

    if not verificar_contrasena(hash_guardado, contrasena):
        return jsonify(error="Credenciales invalidas"), 401

    token = crear_token(user_id, rol)
    return jsonify(token=token, rol=rol), 200
