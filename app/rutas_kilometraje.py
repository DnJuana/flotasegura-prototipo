"""Servicio de Registros: registro de kilometraje (RF1).

Responsable: Integrante D.

Es el flujo principal del diagrama de secuencia de la Evaluacion 2:
validar -> guardar registro -> actualizar camion -> calcular (Strategy)
-> cambiar estado -> notificar (Observer).
"""
from datetime import date

from flask import Blueprint, current_app, g, jsonify, request

from .alertas import (NotificadorConductor, NotificadorJefeFlota, SujetoCamion,
                      peor_estado)
from .db import get_db
from .estrategias import OPERATIVO, obtener_estrategia
from .permisos import login_requerido, puede_acceder_a_camion
from .repositorio import (actualizar_estado_camion, buscar_camion,
                          guardar_registro_kilometraje, planes_de_camion)

bp = Blueprint("kilometraje", __name__)

KM_MAXIMO = 2_000_000  # tope de cordura para un camion


def validar_kilometraje(valor, km_actual: int):
    """Valida el kilometraje informado. Devuelve (ok, mensaje_error).

    Reglas:
      - debe ser un numero entero (no texto, no decimal, no booleano, no nulo)
      - no puede ser negativo
      - no puede ser menor al kilometraje actual del camion
      - no puede superar KM_MAXIMO

    Regla del caso limite (CP-16): un km IGUAL al actual se acepta.
    """
    if isinstance(valor, bool) or not isinstance(valor, int):
        return False, "el kilometraje debe ser un numero entero"
    if valor < 0:
        return False, "el kilometraje no puede ser negativo"
    if valor < km_actual:
        return False, f"el kilometraje no puede ser menor al actual ({km_actual})"
    if valor > KM_MAXIMO:
        return False, f"el kilometraje no puede superar {KM_MAXIMO}"
    return True, ""


def _a_json(proxima):
    """Convierte un ProximaMantencion en un dict serializable a JSON."""
    return {
        "plan_id": proxima.plan_id,
        "tipo": proxima.tipo,
        "km_restantes": proxima.km_restantes,
        "dias_restantes": proxima.dias_restantes,
        "fecha_estimada": proxima.fecha_estimada.isoformat() if proxima.fecha_estimada else None,
        "estado": proxima.estado,
    }


@bp.post("/camiones/<int:camion_id>/kilometraje")
@login_requerido
def registrar_kilometraje(camion_id):
    """POST /camiones/<id>/kilometraje  -  cuerpo JSON: {"kilometraje": 152300}

    Requiere token. Respuestas:
      201 {"camion_id", "km_actual", "estado", "proximas_mantenciones": [...]}
      400 kilometraje invalido
      401 sin token o token invalido            (lo responde login_requerido)
      403 el camion no esta asignado al conductor
      404 el camion no existe
    """
    camion = buscar_camion(camion_id)
    if camion is None:
        return jsonify(error="el camion no existe"), 404

    usuario = g.usuario
    if not puede_acceder_a_camion(usuario, camion):
        current_app.logger.warning(
            "acceso denegado: usuario %s intento registrar km en el camion %s",
            usuario.get("usuario_id"), camion_id)
        return jsonify(error="el camion no esta asignado a este usuario"), 403

    cuerpo = request.get_json(silent=True)
    if not isinstance(cuerpo, dict) or "kilometraje" not in cuerpo:
        return jsonify(error='se espera un JSON con la clave "kilometraje"'), 400

    valor = cuerpo["kilometraje"]
    ok, mensaje = validar_kilometraje(valor, camion["km_actual"])
    if not ok:
        return jsonify(error=mensaje), 400

    # Guarda el registro y actualiza km_actual (una sola transaccion).
    guardar_registro_kilometraje(camion_id, usuario["usuario_id"], valor)

    # Strategy: cada plan se calcula con la estrategia que le corresponde.
    hoy = date.today()
    proximas = [
        obtener_estrategia(plan["tipo_calculo"]).calcular(plan, valor, hoy)
        for plan in planes_de_camion(camion_id)
    ]

    nuevo_estado = peor_estado(proximas)
    cambio = nuevo_estado != camion["estado"]

    # Observer: solo se avisa cuando el estado CAMBIA a amarillo o rojo.
    if cambio and nuevo_estado != OPERATIVO:
        sujeto = SujetoCamion(camion)
        sujeto.suscribir(NotificadorJefeFlota(get_db()))
        sujeto.suscribir(NotificadorConductor(get_db()))
        for proxima in proximas:
            if proxima.estado != OPERATIVO:
                sujeto.notificar(proxima)

    actualizar_estado_camion(camion_id, nuevo_estado)

    return jsonify(
        camion_id=camion_id,
        km_actual=valor,
        estado=nuevo_estado,
        proximas_mantenciones=[_a_json(p) for p in proximas],
    ), 201
