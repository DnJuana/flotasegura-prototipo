"""Consulta de estado del camion y de alertas (RF4).

Responsable: Integrante E.
"""
from flask import Blueprint, jsonify

bp = Blueprint("estado", __name__)


@bp.get("/camiones/<int:camion_id>/estado")
def estado_camion(camion_id):
    """GET /camiones/<id>/estado

    Requiere token. El conductor solo ve su camion; el jefe de flota, todos.
      200 {"camion_id", "patente", "km_actual", "estado", "color"}
          color: operativo=verde, alerta_temprana=amarillo, mantencion_vencida=rojo
      401 / 403 / 404 igual que en el registro de kilometraje

    TODO (E).
    """
    return jsonify(error="consulta de estado pendiente de implementar"), 501


@bp.get("/alertas")
def listar_alertas():
    """GET /alertas

    Requiere token. Cada usuario ve solo las alertas dirigidas a el
    (destinatario_id = su id).
      200 [{"id", "camion_id", "nivel", "mensaje", "fecha"}, ...]

    TODO (E).
    """
    return jsonify(error="listado de alertas pendiente de implementar"), 501
