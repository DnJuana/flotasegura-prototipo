"""Control de acceso por rol - RBAC (RF9 y RNF de seguridad).

Responsable: Integrante F.

Decoradores que protegen los endpoints. Usan leer_token() de auth.py.
El token llega en la cabecera:  Authorization: Bearer <token>
"""
from functools import wraps


def login_requerido(vista):
    """Rechaza con 401 las peticiones sin token o con token invalido.

    TODO (F): leer la cabecera Authorization, validar con leer_token() y
    dejar los datos del usuario en flask.g.usuario para la vista.
    """
    @wraps(vista)
    def envoltura(*args, **kwargs):
        raise NotImplementedError("login_requerido pendiente")
    return envoltura


def rol_requerido(*roles_permitidos):
    """Rechaza con 403 si el rol del usuario no esta en roles_permitidos.

    Uso:
        @bp.get("/alertas")
        @login_requerido
        @rol_requerido("jefe_flota")
        def listar_alertas(): ...

    TODO (F).
    """
    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            raise NotImplementedError("rol_requerido pendiente")
        return envoltura
    return decorador


def puede_acceder_a_camion(usuario: dict, camion: dict) -> bool:
    """Regla del RNF de seguridad de la Evaluacion 2:
    - un conductor solo accede a su camion asignado;
    - el jefe de flota accede a todos.

    TODO (F).
    """
    raise NotImplementedError("puede_acceder_a_camion pendiente")
