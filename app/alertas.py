"""PATRON OBSERVER - Servicio de Alertas (RF4).

Responsable: Integrante B.

SujetoCamion es el sujeto observado; los notificadores son los observadores.
Cuando el estado del camion pasa a alerta temprana o mantencion vencida,
el sujeto notifica y cada observador guarda una alerta en la tabla alertas.

Nota para el informe: en la Evaluacion 2 las alertas salian por push y
correo (Firebase / SendGrid). En el prototipo se guardan en la base de
datos; eso va al registro de cambios de componentes y despliegue.
"""
from abc import ABC, abstractmethod

from .estrategias import ProximaMantencion


class ObservadorMantencion(ABC):
    """Interfaz que implementa todo el que quiera recibir alertas."""

    @abstractmethod
    def actualizar(self, camion: dict, proxima: ProximaMantencion) -> None:
        """Recibe el aviso de que un camion alcanzo el umbral de un plan."""


class SujetoCamion:
    """Sujeto del patron: mantiene la lista de observadores de un camion."""

    def __init__(self, camion: dict):
        self.camion = camion
        self._observadores: list[ObservadorMantencion] = []

    def suscribir(self, observador: ObservadorMantencion) -> None:
        # TODO (B): agregar el observador sin duplicarlo.
        if observador not in self._observadores:
            self._observadores.append(observador)

    def desuscribir(self, observador: ObservadorMantencion) -> None:
        # TODO (B): quitar el observador si esta suscrito.
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, proxima: ProximaMantencion) -> None:
        # TODO (B): llamar a actualizar() de cada observador.
        for observador in self._observadores:
            observador.actualizar(self.camion, proxima)


class NotificadorJefeFlota(ObservadorMantencion):
    """Guarda una alerta dirigida a cada usuario con rol jefe_flota."""

    def __init__(self, conexion):
        self.conexion = conexion

    def actualizar(self, camion: dict, proxima: ProximaMantencion) -> None:
        # TODO (B): insertar en la tabla alertas (usar consultas parametrizadas).
        raise NotImplementedError("NotificadorJefeFlota pendiente")


class NotificadorConductor(ObservadorMantencion):
    """Guarda una alerta dirigida al conductor asignado al camion."""

    def __init__(self, conexion):
        self.conexion = conexion

    def actualizar(self, camion: dict, proxima: ProximaMantencion) -> None:
        # TODO (B): insertar en la tabla alertas. Si el camion no tiene
        # conductor asignado, no se genera alerta para conductor.
        raise NotImplementedError("NotificadorConductor pendiente")


def peor_estado(resultados: list[ProximaMantencion]) -> str:
    """Estado del camion = el peor estado entre todos sus planes.

    TODO (B): mantencion_vencida > alerta_temprana > operativo.
    Una lista vacia equivale a 'operativo'.
    """
    raise NotImplementedError("peor_estado pendiente")
