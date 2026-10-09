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

    def __init__(self, camion_dict):
        self.camion = camion_dict
        self._observadores= []

    def suscribir(self, observador):
        # TODO (B): agregar el observador sin duplicarlo.
        if observador not in self._observadores:
            self._observadores.append(observador)

    def desuscribir(self, observador):
        # TODO (B): quitar el observador si esta suscrito.
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, plan_mantencion):
        # TODO (B): llamar a actualizar() de cada observador.
        for observador in self._observadores:
            observador.actualizar(self.camion, plan_mantencion)


class NotificadorJefeFlota:
    """Guarda una alerta dirigida a cada usuario con rol jefe_flota."""

    def __init__(self, db_conexion):
        self.conexion = db_conexion

    def actualizar(self, camion, plan_mantencion):
        # TODO (B): insertar en la tabla alertas (usar consultas parametrizadas).
        cursor = self.conexion.cursor()
        mensaje = f"Alerta para jefe de Flota: Camion {camion['patente']} en estado {plan_mantencion.estado} "
        cursor.execute(
            "INSERT INTO alertas (camion_id, mensaje) VALUES (?,?)",
            (camion['id'], mensaje)
        )
        self.conexion.commit()


class NotificadorConductor:
    """Guarda una alerta dirigida al conductor asignado al camion."""

    def __init__(self, db_conexion):
        self.conexion = db_conexion

    def actualizar(self, camion, plan_mantencion):
        # TODO (B): insertar en la tabla alertas. Si el camion no tiene 
        if not camion.get('conductor_id'):
            return 
        cursor = self.conexion.cursor()
        mensaje = f"Estimado conductor, su camión {camion['patente']} requiere atención: {plan_mantencion.estado}"
        cursor.execute(
            "INSERT INTO alertas (camion_id, mensaje) VALUES(?,?)",(camion['id'], mensaje)
        )
        self.conexion.commit()


def peor_estado(planes):
    """Estado del camion = el peor estado entre todos sus planes"""
    if not planes:
        return "operativo"
    
    orden_prioridad ={
        "mantencion_vencida": 3,
        "alerta_temprana": 2,
        "operativo": 1  
    }
    
    peor = max(planes, key=lambda p: orden_prioridad.get(p.estado, 0))
    return peor.estado
