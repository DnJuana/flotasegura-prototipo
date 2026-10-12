"""Consulta de estado del camion y de alertas (RF4).

Responsable: Integrante E (Felipe Aravena).

Los dos endpoints son de solo lectura y exigen token. El semaforo traduce
el estado guardado en la base (que calcula el registro de kilometraje con
los patrones Strategy y Observer) al color que ve el usuario.
"""
from flask import Blueprint, g, jsonify

from . import repositorio
from .permisos import login_requerido, puede_acceder_a_camion

bp = Blueprint("estado", __name__)

# Estado del camion -> color del semaforo (RF5 de la Evaluacion 2).
COLORES = {
    "operativo": "verde",
    "alerta_temprana": "amarillo",
    "mantencion_vencida": "rojo",
}


@bp.get("/camiones/<int:camion_id>/estado")
@login_requerido
def estado_camion(camion_id):
    """GET /camiones/<id>/estado

    El conductor solo ve su camion asignado; el jefe de flota, todos.
      200 {"camion_id", "patente", "km_actual", "estado", "color"}
      401 sin token o token invalido
      403 el camion no esta asignado al conductor
      404 el camion no existe
    """
    camion = repositorio.buscar_camion(camion_id)
    if camion is None:
        return jsonify(error="El camion especificado no existe"), 404

    if not puede_acceder_a_camion(g.usuario, camion):
        # El rechazo no incluye ningun dato del camion.
        return jsonify(error="No tiene permiso para consultar este camion"), 403

    return jsonify(
        camion_id=camion["id"],
        patente=camion["patente"],
        km_actual=camion["km_actual"],
        estado=camion["estado"],
        color=COLORES[camion["estado"]],
    ), 200


@bp.get("/alertas")
@login_requerido
def listar_alertas():
    """GET /alertas

    Cada usuario ve solo las alertas dirigidas a el. El destinatario se
    toma del token, nunca de un parametro de la peticion, para que nadie
    pueda pedir las alertas de otro usuario.
      200 [{"id", "camion_id", "nivel", "mensaje", "fecha"}, ...]
          de la mas reciente a la mas antigua; lista vacia si no hay
      401 sin token o token invalido
    """
    alertas = repositorio.alertas_de_usuario(g.usuario["id"])
    return jsonify(
        [
            {
                "id": alerta["id"],
                "camion_id": alerta["camion_id"],
                "nivel": alerta["nivel"],
                "mensaje": alerta["mensaje"],
                "fecha": alerta["fecha"],
            }
            for alerta in alertas
        ]
    ), 200
