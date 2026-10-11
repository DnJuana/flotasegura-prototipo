"""Servicio de Autenticacion: inicio de sesion (RF9).

Responsable: Integrante C.

Incluye el hash de contrasenas, la emision y lectura del token de sesion
y el endpoint POST /login.
"""
from flask import Blueprint, jsonify, current_app, request
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
from .repositorio import buscar_usuario_por_nombre

bp = Blueprint("auth", __name__)


def hash_contrasena(contrasena: str) -> str:
    """Devuelve el hash de la contrasena para guardarlo en la base.

    TODO (C): usar werkzeug.security.generate_password_hash.
    Nunca se guarda la contrasena en texto plano (RNF de seguridad).
    """
    return generate_password_hash(contrasena)


def verificar_contrasena(hash_guardado: str, contrasena: str) -> bool:
    """Verifica si la contraseña coincide con el hash guardado."""
    return check_password_hash(hash_guardado, contrasena)



def crear_token(usuario_id: int, rol: str) -> str:
    """Crea un token firmado con el ID y el rol del usuario."""
    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    return serializer.dumps({
        "usuario_id": usuario_id,
        "rol": rol
    })




def leer_token(token: str):
    """Valida la firma y duración del token de sesión."""
    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    try:
        datos = serializer.loads(
            token,
            max_age=current_app.config["TOKEN_DURACION_SEG"]
        )

        if not isinstance(datos, dict):
            return None

        if not isinstance(datos.get("usuario_id"), int):
            return None

        if isinstance(datos["usuario_id"], bool):
            return None

        if not isinstance(datos.get("rol"), str):
            return None

        return {
            "usuario_id": datos["usuario_id"],
            "rol": datos["rol"]
        }

    except (BadSignature, SignatureExpired, ValueError, TypeError):
        return None


@bp.post("/login")
def login():
    """Autentica al usuario y devuelve un token de sesión."""

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify(error="Solicitud JSON inválida"), 400

    usuario = datos.get("usuario")
    contrasena = datos.get("contrasena")

    if (
        not isinstance(usuario, str)
        or not usuario.strip()
        or not isinstance(contrasena, str)
        or not contrasena
    ):
        return jsonify(
            error="Usuario y contraseña son obligatorios"
        ), 400

    registro = buscar_usuario_por_nombre(usuario.strip())

    if registro is None or not verificar_contrasena(
        registro["hash_contrasena"], contrasena
    ):
        return jsonify(error="Credenciales inválidas"), 401

    token = crear_token(registro["id"], registro["rol"])

    return jsonify(
        token=token,
        rol=registro["rol"]
    ), 200
