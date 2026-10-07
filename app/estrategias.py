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
from datetime import date
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
        # TODO (A):
        #   km_restantes = km_ultima_mantencion + intervalo_km - km_actual
        #   estado = MANTENCION_VENCIDA si km_restantes <= 0
        #            ALERTA_TEMPRANA    si km_restantes <= umbral_aviso_km
        #            OPERATIVO          en otro caso
        raise NotImplementedError("CalculoPorKm pendiente")


class CalculoPorFecha(EstrategiaCalculo):
    """Mantencion cada N dias (ej. revision de frenos cada 180 dias)."""

    def calcular(self, plan: dict, km_actual: int, hoy: date) -> ProximaMantencion:
        # TODO (A):
        #   fecha_estimada = fecha_ultima_mantencion + intervalo_dias
        #   dias_restantes = (fecha_estimada - hoy).days
        #   estado segun dias_restantes y umbral_aviso_dias
        raise NotImplementedError("CalculoPorFecha pendiente")


def obtener_estrategia(tipo_calculo: str) -> EstrategiaCalculo:
    """Devuelve la estrategia que corresponde al campo tipo_calculo del plan.

    TODO (A): 'km' -> CalculoPorKm, 'fecha' -> CalculoPorFecha.
    Un valor desconocido debe lanzar ValueError.
    """
    raise NotImplementedError("obtener_estrategia pendiente")
