"""Servicio de Registros: registro de kilometraje (RF1).

Responsable: Integrante D.

Es el flujo principal del diagrama de secuencia de la Evaluacion 2:
validar -> guardar registro -> actualizar camion -> calcular (Strategy)
-> cambiar estado -> notificar (Observer).
"""
from flask import Blueprint, jsonify

bp = Blueprint("kilometraje", __name__)

KM_MAXIMO = 2_000_000  # tope de cordura para un camion


def validar_kilometraje(valor, km_actual: int):
    """Valida el kilometraje informado. Devuelve (ok, mensaje_error).

    TODO (D). Reglas:
      - debe ser un numero entero (no texto, no decimal, no booleano, no nulo)
      - no puede ser negativo
      - no puede ser menor al kilometraje actual del camion
      - no puede superar KM_MAXIMO
    """
    raise NotImplementedError("validar_kilometraje pendiente")


@bp.post("/camiones/<int:camion_id>/kilometraje")
def registrar_kilometraje(camion_id):
    """POST /camiones/<id>/kilometraje  -  cuerpo JSON: {"kilometraje": 152300}

    Requiere token. Respuestas esperadas:
      201 {"camion_id", "km_actual", "estado", "proximas_mantenciones": [...]}
      400 kilometraje invalido
      401 sin token o token invalido
      403 el camion no esta asignado al conductor
      404 el camion no existe

    TODO (D). Pasos:
      1. Proteger con @login_requerido (permisos.py).
      2. Buscar el camion (repositorio.py) -> 404 si no existe.
      3. puede_acceder_a_camion() -> 403 si no corresponde.
      4. validar_kilometraje() -> 400 si falla.
      5. Guardar el registro y actualizar km_actual.
      6. Por cada plan del camion: obtener_estrategia(...).calcular(...).
      7. Calcular peor_estado(); si cambio a amarillo o rojo, crear el
         SujetoCamion, suscribir los dos notificadores y notificar().
      8. Guardar el nuevo estado y responder 201.
    """
    return jsonify(error="registro de kilometraje pendiente de implementar"), 501
