"""Acceso a datos: todas las consultas SQL del prototipo.

Responsable: Integrante E.

Regla del grupo: las consultas siempre usan parametros (?), nunca se arma
el SQL concatenando texto que viene del usuario.
"""
from .db import get_db


def buscar_usuario_por_nombre(nombre_usuario: str):
    """Devuelve la fila del usuario o None. La usa el login (C). TODO (E)."""
    raise NotImplementedError("buscar_usuario_por_nombre pendiente")


def buscar_camion(camion_id: int):
    """Devuelve la fila del camion o None. TODO (E)."""
    raise NotImplementedError("buscar_camion pendiente")


def planes_de_camion(camion_id: int) -> list:
    """Devuelve los planes de mantencion del camion. TODO (E)."""
    raise NotImplementedError("planes_de_camion pendiente")


def guardar_registro_kilometraje(camion_id: int, conductor_id: int, kilometraje: int) -> int:
    """Inserta el registro y actualiza km_actual del camion en una misma
    transaccion. Devuelve el id del registro. TODO (E)."""
    raise NotImplementedError("guardar_registro_kilometraje pendiente")


def actualizar_estado_camion(camion_id: int, estado: str) -> None:
    """TODO (E)."""
    raise NotImplementedError("actualizar_estado_camion pendiente")


def alertas_de_usuario(usuario_id: int) -> list:
    """Alertas dirigidas al usuario, de la mas reciente a la mas antigua. TODO (E)."""
    raise NotImplementedError("alertas_de_usuario pendiente")
