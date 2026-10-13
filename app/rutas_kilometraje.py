"""Servicio de Registros: registro de kilometraje (RF1).

Responsable: Integrante D.
"""
from datetime import date
from flask import Blueprint, jsonify, request, g, current_app

from . import repositorio
from . import estrategias
from . import alertas
from .permisos import login_requerido, puede_acceder_a_camion

bp = Blueprint("kilometraje", __name__)

KM_MAXIMO = 2_000_000  # Tope de cordura para un camión


def validar_kilometraje(valor, km_actual: int):
    """Valida el kilometraje informado. Devuelve (ok, mensaje_error)."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        return False, "El kilometraje debe ser un número entero válido."

    if valor < 0:
        return False, "El kilometraje no puede ser negativo."

    if valor < km_actual:
        return False, f"El kilometraje ({valor}) no puede ser menor al actual ({km_actual})."

    if valor > KM_MAXIMO:
        return False, f"El kilometraje excede el límite máximo permitido ({KM_MAXIMO})."

    return True, None


@bp.post("/camiones/<int:camion_id>/kilometraje")
@login_requerido
def registrar_kilometraje(camion_id):
    """POST /camiones/<id>/kilometraje"""
    # CP-33: Control de tamaño de payload (máximo 1 MB)
    if (request.content_length and request.content_length > 1_000_000) or (request.data and len(request.data) > 1_000_000):
        return jsonify(error="El cuerpo de la petición es demasiado grande"), 413

    # CP-31: Manejo de IDs fuera de rango
    if camion_id > 2_147_483_647:
        return jsonify(error="Camión no encontrado"), 404

    # 1. Verificar existencia del camión (404)
    camion = repositorio.buscar_camion(camion_id)
    if not camion:
        return jsonify(error="El camión especificado no existe"), 404

    # 2. Control de acceso según rol y asignación (403)
    usuario = g.usuario
    if not puede_acceder_a_camion(usuario, camion):
        return jsonify(error="No tiene permiso para registrar en este camión"), 403

    # 3. Validación de estructura JSON (400 / CP-28)
    datos = request.get_json(silent=True)
    if datos is None or not isinstance(datos, dict) or "kilometraje" not in datos:
        return jsonify(error="Campo 'kilometraje' es requerido en el JSON"), 400

    km_ingresado = datos["kilometraje"]

    # 4. Validar valor del kilometraje (400)
    ok, error_msg = validar_kilometraje(km_ingresado, camion["km_actual"])
    if not ok:
        return jsonify(error=error_msg), 400

    # 5. Persistir el nuevo registro y actualizar el camión
    repositorio.guardar_registro_kilometraje(camion_id, usuario["id"], km_ingresado)
    camion["km_actual"] = km_ingresado

    # 6. Evaluar planes con el Patrón Strategy
    planes = repositorio.planes_de_camion(camion_id)
    proximas_mantenciones = []
    hoy = date.today()

    for plan in planes:
        estrategia = estrategias.obtener_estrategia(plan["tipo_calculo"])
        proxima = estrategia.calcular(plan, km_ingresado, hoy)
        proximas_mantenciones.append(proxima)

    # 7. Determinar el peor estado entre todos los planes
    nuevo_estado = alertas.peor_estado(proximas_mantenciones)
    estado_anterior = camion["estado"]

    # 8. Notificar mediante el Patrón Observer solo si cambió a alerta o mantenimiento
    if nuevo_estado != estado_anterior and nuevo_estado in (
        estrategias.ALERTA_TEMPRANA,
        estrategias.MANTENCION_VENCIDA,
    ):
        sujeto = alertas.SujetoCamion(camion)
        db_conn = repositorio.get_db()
        sujeto.suscribir(alertas.NotificadorJefeFlota(db_conn))
        sujeto.suscribir(alertas.NotificadorConductor(db_conn))

        for proxima in proximas_mantenciones:
            if proxima.estado != estrategias.OPERATIVO:
                try:
                    sujeto.notificar(proxima)
                except Exception as e:
                    # CP-34: Tolerancia a fallos en notificación
                    current_app.logger.error(f"Error al enviar notificación: {e}")

    # 9. Guardar nuevo estado y retornar respuesta 201
    repositorio.actualizar_estado_camion(camion_id, nuevo_estado)

    proximas_json = [
        {
            "plan_id": p.plan_id,
            "tipo": p.tipo,
            "km_restantes": p.km_restantes,
            "dias_restantes": p.dias_restantes,
            "fecha_estimada": p.fecha_estimada.isoformat() if p.fecha_estimada else None,
            "estado": p.estado,
        }
        for p in proximas_mantenciones
    ]

    return (
        jsonify(
            {
                "camion_id": camion_id,
                "km_actual": km_ingresado,
                "estado": nuevo_estado,
                "proximas_mantenciones": proximas_json,
            }
        ),
        201,
    )
