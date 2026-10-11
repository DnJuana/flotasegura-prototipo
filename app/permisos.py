"""Control de acceso por rol - RBAC (RF9 y RNF de seguridad).

Responsable: Integrante F.

Decoradores que protegen los endpoints. Usan leer_token() de auth.py.
El token llega en la cabecera:   Authorization: Bearer <token>
"""
from functools import wraps
from flask import request, jsonify, g
from app.auth import leer_token


def login_requerido(vista):
    """Rechaza con 401 las peticiones sin token o con token invalido."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token ausente o mal formado"}), 401
        
        token = auth_header.split(" ")[1]
        usuario = leer_token(token)
        if not usuario:
            return jsonify({"error": "Token invalido o expirado"}), 401
            
        g.usuario = usuario
        return vista(*args, **kwargs)
    return envoltura


def rol_requerido(*roles_permitidos):
    """Rechaza con 403 si el rol del usuario no esta en roles_permitidos."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            usuario = getattr(g, "usuario", None)
            if not usuario or usuario.get("rol") not in roles_permitidos:
                return jsonify({"error": "Acceso denegado por rol"}), 403
            return vista(*args, **kwargs)
        return envoltura
    return decorador


def puede_acceder_a_camion(usuario: dict, camion: dict) -> bool:
    """Regla del RNF de seguridad de la Evaluacion 2:
    - un conductor solo accede a su camion asignado;
    - el jefe de flota accede a todos.
    """
    if not usuario or not camion:
        return False
    
    rol = usuario.get("rol")
    if rol == "jefe_flota":
        return True
    if rol == "conductor":
        return str(camion.get("conductor_id")) == str(usuario.get("id")) or str(camion.get("patente")) == str(usuario.get("patente_asignada"))
    
    return False