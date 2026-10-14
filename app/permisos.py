"""Control de acceso por rol - RBAC (RF9 y RNF de seguridad).

Responsable: Integrante F.

Decoradores que protegen los endpoints. Usan leer_token() de auth.py.
El token llega en la cabecera:  Authorization: Bearer <token>
"""
from functools import wraps
from flask import request, jsonify, g
from .auth import leer_token
from .db import get_db


def login_requerido(vista):
    """Rechaza con 401 las peticiones sin token, token invalido o usuario inexistente."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify(error="Token no proporcionado o formato invalido"), 401

        token = auth_header.split(" ", 1)[1].strip()
        datos = leer_token(token)
        if not datos or not isinstance(datos, dict):
            return jsonify(error="Token invalido o expirado"), 401

        usuario_id = datos.get("usuario_id")
        db = get_db()
        cursor = db.execute("SELECT id, rol FROM usuarios WHERE id = ?", (usuario_id,))
        user = cursor.fetchone()
        if user is None:
            return jsonify(error="Usuario del token no existe"), 401

        try:
            u_id = user["id"]
            u_rol = user["rol"]
        except (TypeError, KeyError):
            u_id = user[0]
            u_rol = user[1]

        g.usuario = {
            "id": u_id,
            "usuario_id": u_id,
            "rol": u_rol,
        }
        return vista(*args, **kwargs)

    return envoltura


def rol_requerido(*roles_permitidos):
    """Rechaza con 403 si el rol del usuario no esta en roles_permitidos."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if not hasattr(g, "usuario") or not g.usuario:
                return jsonify(error="Autenticacion requerida"), 401
            if g.usuario.get("rol") not in roles_permitidos:
                return jsonify(error="Acceso denegado por rol"), 403
            return vista(*args, **kwargs)

        return envoltura

    return decorador


def puede_acceder_a_camion(usuario: dict, camion: dict) -> bool:
    """Regla del RNF de seguridad:
    - un conductor solo accede a su camion asignado;
    - el jefe de flota accede a todos.
    """
    if not usuario or not camion:
        return False
    rol = usuario.get("rol")
    if rol == "jefe_flota":
        return True
    if rol == "conductor":
        u_id = usuario.get("id") if usuario.get("id") is not None else usuario.get("usuario_id")
        return camion.get("conductor_id") == u_id
    return False
