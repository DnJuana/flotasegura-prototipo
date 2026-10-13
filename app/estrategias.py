"""PATRON STRATEGY - Motor de Calculo de Mantenciones (RF3).

Responsable: Integrante A.

La interfaz EstrategiaCalculo y el resultado ProximaMantencion ya estan
definidos (son el contrato que usan los demas frentes). Falta implementar
las dos estrategias concretas y la funcion que elige cual usar.

Nota para el informe: en la Evaluacion 2 habia tres estrategias. En el
prototipo se implementan dos (km y fecha); CalculoPorRuta queda fuera y
eso va al registro de cambios del diagrama de clases.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

OPERATIVO = "operativo"
ALERTA_TEMPRANA = "alerta_temprana"
MANTENCION_VENCIDA = "mantencion_vencida"


@dataclass
class ProximaMantencion:
    """Resultado del calculo para un plan de mantencion."""

    plan_id: int
    tipo: str                            # aceite, frenos, neumaticos
    km_restantes: Optional[int] = None   # solo en calculo por km
    dias_restantes: Optional[int] = None # solo en calculo por fecha
    fecha_estimada: Optional[date] = None
    estado: str = OPERATIVO              # OPERATIVO | ALERTA_TEMPRANA | MANTENCION_VENCIDA


def _requerir(plan: dict, *campos: str) -> None:
    """Verifica que el plan tenga cargados los campos que usa la estrategia."""
    faltantes = [c for c in campos if plan[c] is None]
    if faltantes:
        raise ValueError(
            f"El plan {plan['id']} no tiene los campos requeridos: {', '.join(faltantes)}"
        )


def _a_fecha(valor) -> date:
    """Convierte AAAA-MM-DD (texto de SQLite) a date; acepta date tal cual."""
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(valor)


def _estado_segun(restante: int, umbral: int) -> str:
    """Regla comun: <= 0 vencida, <= umbral alerta temprana, resto operativo."""
    if restante <= 0:
        return MANTENCION_VENCIDA
    if restante <= umbral:
        return ALERTA_TEMPRANA
    return OPERATIVO


class EstrategiaCalculo(ABC):
    """Interfaz comun: cada regla de mantencion es una estrategia."""

    @abstractmethod
    def calcular(self, plan: dict, km_actual: int, hoy: date) -> ProximaMantencion:
        """Calcula la proxima mantencion de un plan.

        plan: fila de la tabla planes_mantencion convertida a dict.
        km_actual: kilometraje actual del camion.
        hoy: fecha contra la que se calcula (se recibe por parametro para
             poder probar con fechas fijas).
        """


class CalculoPorKm(EstrategiaCalculo):
    """Mantencion cada N kilometros (ej. aceite cada 10.000 km)."""

    def calcular(self, plan: dict, km_actual: int, hoy: date) -> ProximaMantencion:
        _requerir(plan, "intervalo_km", "km_ultima_mantencion", "umbral_aviso_km")
        km_restantes = (
            plan["km_ultima_mantencion"] + plan["intervalo_km"] - km_actual
        )
        return ProximaMantencion(
            plan_id=plan["id"],
            tipo=plan["tipo"],
            km_restantes=km_restantes,
            estado=_estado_segun(km_restantes, plan["umbral_aviso_km"]),
        )


class CalculoPorFecha(EstrategiaCalculo):
    """Mantencion cada N dias (ej. revision de frenos cada 180 dias)."""

    def calcular(self, plan: dict, km_actual: int, hoy: date) -> ProximaMantencion:
        _requerir(plan, "intervalo_dias", "fecha_ultima_mantencion", "umbral_aviso_dias")
        fecha_estimada = _a_fecha(plan["fecha_ultima_mantencion"]) + timedelta(
            days=plan["intervalo_dias"]
        )
        dias_restantes = (fecha_estimada - hoy).days
        return ProximaMantencion(
            plan_id=plan["id"],
            tipo=plan["tipo"],
            dias_restantes=dias_restantes,
            fecha_estimada=fecha_estimada,
            estado=_estado_segun(dias_restantes, plan["umbral_aviso_dias"]),
        )


_ESTRATEGIAS = {"km": CalculoPorKm, "fecha": CalculoPorFecha}


def obtener_estrategia(tipo_calculo: str) -> EstrategiaCalculo:
    """Devuelve la estrategia que corresponde al campo tipo_calculo del plan.

    'km' -> CalculoPorKm, 'fecha' -> CalculoPorFecha.
    Un valor desconocido lanza ValueError.
    """
    try:
        return _ESTRATEGIAS[tipo_calculo]()
    except (KeyError, TypeError):
        raise ValueError(f"tipo_calculo desconocido: {tipo_calculo!r}") from None
