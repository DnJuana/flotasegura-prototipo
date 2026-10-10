"""
FlotaSegura - Módulo de Autenticación
Autor: Yerko Morales

Funciones principales:
- Hash seguro de contraseñas.
- Validación de contraseña.
- Inicio de sesión.
- Generación de token.
- Validación de token.
- Control de acceso por roles (RBAC).

Prototipo académico - Ingeniería de Software.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Dict, List


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Para un sistema real esta clave debe guardarse como variable
# de entorno y nunca publicarse en GitHub.
SECRET_KEY = os.getenv(
    "FLOTASEGURA_SECRET",
    "clave-academica-flotasegura-2026"
)

TOKEN_DURATION_SECONDS = 3600  # 1 hora


# ============================================================
# EXCEPCIONES
# ============================================================

class AuthError(Exception):
    """Error general del módulo de autenticación."""
    pass


class InvalidCredentialsError(AuthError):
    """Usuario o contraseña incorrectos."""
    pass


class InvalidTokenError(AuthError):
    """Token inválido, manipulado o vencido."""
    pass


class PermissionDeniedError(AuthError):
    """Usuario autenticado pero sin permisos suficientes."""
    pass


# ============================================================
# FUNCIONES PARA PASSWORD
# ============================================================

def hash_password(password: str, salt: str = None) -> Dict[str, str]:
    """
    Genera un hash seguro de la contraseña utilizando PBKDF2-HMAC-SHA256.

    Retorna:
        {
            "salt": "...",
            "hash": "..."
        }
    """

    if not password:
        raise ValueError("La contraseña no puede estar vacía.")

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    )

    return {
        "salt": salt,
        "hash": password_hash.hex()
    }


def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    """
    Compara una contraseña ingresada con el hash almacenado.
    """

    calculated = hash_password(password, salt)["hash"]

    return hmac.compare_digest(
        calculated,
        stored_hash
    )


# ============================================================
# BASE DE USUARIOS DEL PROTOTIPO
# ============================================================

def create_demo_user(username: str, password: str, role: str) -> Dict:
    """
    Crea un usuario de demostración almacenando solo el hash.
    """

    password_data = hash_password(password)

    return {
        "username": username,
        "role": role,
        "salt": password_data["salt"],
        "password_hash": password_data["hash"]
    }


USERS = {
    "conductor1": create_demo_user(
        "conductor1",
        "Camion123",
        "conductor"
    ),

    "jefe1": create_demo_user(
        "jefe1",
        "Flota123",
        "jefe_flota"
    ),

    "gerente1": create_demo_user(
        "gerente1",
        "Gerencia123",
        "gerente"
    )
}


# ============================================================
# UTILIDADES DEL TOKEN
# ============================================================

def _base64_encode(data: bytes) -> str:
    """
    Codificación Base64 segura para URL.
    """

    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64_decode(data: str) -> bytes:
    """
    Decodifica Base64 agregando padding si es necesario.
    """

    padding = "=" * (-len(data) % 4)

    return base64.urlsafe_b64decode(data + padding)


# ============================================================
# GENERACIÓN DE TOKEN
# ============================================================

def generate_token(
    username: str,
    role: str,
    duration_seconds: int = TOKEN_DURATION_SECONDS
) -> str:
    """
    Genera un token firmado con HMAC-SHA256.
    """

    now = int(time.time())

    payload = {
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + duration_seconds
    }

    payload_json = json.dumps(
        payload,
        separators=(",", ":")
    ).encode("utf-8")

    payload_encoded = _base64_encode(payload_json)

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        payload_encoded.encode("utf-8"),
        hashlib.sha256
    ).digest()

    signature_encoded = _base64_encode(signature)

    return f"{payload_encoded}.{signature_encoded}"


# ============================================================
# VALIDACIÓN DE TOKEN
# ============================================================

def validate_token(token: str) -> Dict:
    """
    Verifica:
    - estructura del token
    - firma
    - fecha de expiración
    - existencia del usuario
    - coincidencia del rol
    """

    if not token:
        raise InvalidTokenError("No se recibió ningún token.")

    try:
        payload_encoded, signature_received = token.split(".")
    except ValueError:
        raise InvalidTokenError(
            "El formato del token es inválido."
        )

    expected_signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        payload_encoded.encode("utf-8"),
        hashlib.sha256
    ).digest()

    expected_signature_encoded = _base64_encode(
        expected_signature
    )

    if not hmac.compare_digest(
        signature_received,
        expected_signature_encoded
    ):
        raise InvalidTokenError(
            "La firma del token es inválida."
        )

    try:
        payload_json = _base64_decode(
            payload_encoded
        ).decode("utf-8")

        payload = json.loads(payload_json)

    except (ValueError, json.JSONDecodeError):
        raise InvalidTokenError(
            "El contenido del token es inválido."
        )

    if payload.get("exp", 0) < int(time.time()):
        raise InvalidTokenError(
            "El token ha expirado."
        )

    username = payload.get("username")
    role = payload.get("role")

    if username not in USERS:
        raise InvalidTokenError(
            "El usuario del token no existe."
        )

    if USERS[username]["role"] != role:
        raise InvalidTokenError(
            "El rol contenido en el token no es válido."
        )

    return payload


# ============================================================
# LOGIN
# ============================================================

def login(username: str, password: str) -> str:
    """
    Autentica al usuario.

    Si las credenciales son correctas:
        retorna un token.

    Si son incorrectas:
        genera InvalidCredentialsError.
    """

    if not username or not password:
        raise InvalidCredentialsError(
            "Usuario y contraseña son obligatorios."
        )

    user = USERS.get(username)

    if user is None:
        raise InvalidCredentialsError(
            "Usuario o contraseña incorrectos."
        )

    valid_password = verify_password(
        password,
        user["salt"],
        user["password_hash"]
    )

    if not valid_password:
        raise InvalidCredentialsError(
            "Usuario o contraseña incorrectos."
        )

    return generate_token(
        username=user["username"],
        role=user["role"]
    )


# ============================================================
# RBAC - CONTROL DE ACCESO POR ROLES
# ============================================================

def require_role(
    token: str,
    allowed_roles: List[str]
) -> Dict:
    """
    Comprueba primero la autenticación y posteriormente
    verifica si el rol puede utilizar la funcionalidad.

    Ejemplo:

    require_role(
        token,
        ["jefe_flota", "gerente"]
    )
    """

    payload = validate_token(token)

    role = payload["role"]

    if role not in allowed_roles:
        raise PermissionDeniedError(
            f"Acceso denegado para el rol '{role}'."
        )

    return payload


# ============================================================
# FUNCIONES SIMULADAS DEL SISTEMA FLOTASEGURA
# ============================================================

def registrar_kilometraje(token: str, kilometraje: int) -> str:
    """
    Acción permitida al conductor.
    """

    require_role(
        token,
        ["conductor"]
    )

    if kilometraje <= 0:
        raise ValueError(
            "El kilometraje debe ser mayor que cero."
        )

    return (
        f"Kilometraje {kilometraje} km "
        f"registrado correctamente."
    )


def gestionar_mantenciones(token: str) -> str:
    """
    Acción exclusiva del Jefe de Flota.
    """

    require_role(
        token,
        ["jefe_flota"]
    )

    return "Acceso concedido a gestión de mantenciones."


def consultar_reportes(token: str) -> str:
    """
    Acción disponible para Jefe de Flota y Gerente.
    """

    require_role(
        token,
        ["jefe_flota", "gerente"]
    )

    return "Acceso concedido a reportes históricos."


# ============================================================
# DEMOSTRACIÓN
# ============================================================

if __name__ == "__main__":

    print("\n==============================")
    print("     FLOTASEGURA - LOGIN")
    print("==============================\n")

    try:

        token = login(
            "jefe1",
            "Flota123"
        )

        print("LOGIN CORRECTO")
        print("Token generado:")
        print(token)

        usuario = validate_token(token)

        print("\nUsuario autenticado:")
        print(usuario["username"])

        print("Rol:")
        print(usuario["role"])

        resultado = gestionar_mantenciones(token)

        print("\nResultado:")
        print(resultado)

    except AuthError as error:

        print("ERROR:")
        print(error)