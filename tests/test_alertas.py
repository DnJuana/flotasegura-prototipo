"""Pruebas del patron Observer (RF4).

Responsable: Integrante B.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
Quitar el pytest.skip al implementarla.
"""
import pytest
from app.alertas import SujetoCamion, NotificadorJefeFlota, NotificadorConductor, peor_estado
from app.estrategias import ProximaMantencion


def test_cp_06_al_cruzar_umbral_se_alerta_a_jefe_y_conductor(db_conexion):
    """CP-06 | Funcional | RF4

    Entrada: notificar() con los dos notificadores suscritos. Esperado: una alerta para el jefe de flota y otra para el conductor.
    """
    camion = {"id":1,"patente": "ABC-12", "conductor_id": 10}
    sujeto = SujetoCamion(camion)
    
    #suscribimos ambos observadores
    sujeto.suscribir(NotificadorJefeFlota(db_conexion))
    sujeto.suscribir(NotificadorConductor(db_conexion))
    
    proxima= ProximaMantencion(pla_id = 1, tipo = "aceite", estado="alerta_temprana", km_restantes=500)
    sujeto.notificar(proxima)
    
    #verificamos que se hayan guardado las alertas en la BD
    curso = db_conexion.curso()
    curso.execute("SELECT COUNT(*) FROM alertas WHERE camion_id = ?", (1,))
    total_alerta = curso.fetchone()[0]
    
    assert total_alerta == 2


def test_cp_07_camion_sin_conductor_solo_alerta_al_jefe(db_conexion):
    """CP-07 | Funcional - caso limite | RF4

    Entrada: camion con conductor_id nulo. Esperado: solo se crea la alerta del jefe de flota, sin error.
    """
    camion = {"id": 2, "patente": "XYZ-99", "conductor_id": None}
    sujeto= SujetoCamion(camion)
    
    sujeto.suscribir(NotificadorJefeFlota(db_conexion))
    sujeto.suscribir(NotificadorConductor(db_conexion))
     
    proxima = ProximaMantencion(plan_id=2, tipo="frenos", estado="Mantencion_vencida", km_restantes =-100)
    sujeto.notificar(proxima)
    
    #solo debe de existir 1 alerta (la del jefe de flota, ya que no hay conductores)
    cursor = db_conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM alertas WHERE camion_id =? ",(2,))
    total_alertas = cursor.fetchone()[0]
    
    assert total_alertas == 1


def test_cp_08_observador_desuscrito_no_recibe_alerta(db_conexion):
    """CP-08 | Funcional | RF4

    Entrada: suscribir, desuscribir y notificar. Esperado: cero alertas para ese observador.
    """
    camion = {"id": 3, "patente": "TEST-03", " conductor_id": 5}
    sujeto= SujetoCamion(camion)
    
    observador = NotificadorJefeFlota(db_conexion)
    sujeto.suscribir(observador)
    sujeto.desuscribir(observador)
    
    proxima = ProximaMantencion(plan_id =3, tipo="neumaticos" "alerta_temprana", km_restante = 200)
    sujeto.notificar(proxima)
    
    cursor = db_conexion.cursor()
    cursor.execute("SELECT COUND(*) FROM alertas WHERE camion_id = ?",(3,))
    total_alertas = cursor.fetchone()[0]
    
    assert total_alertas == 0


def test_cp_09_peor_estado_entre_varios_planes():
    """CP-09 | Funcional | RF4

    Entrada: un plan operativo y otro vencido. Esperado: mantencion_vencida.
    """
    planes=[
        ProximaMantencion(plan_id=1, tipo="aceite", estado="operativo", km_restante=5000),
        ProximaMantencion(plan_id=2, tipo="frenos", estado="mantencion_vencida", km_restante=-10)
    ]
    
    resultado= peor_estado(planes)
    assert resultado == "mantencion_vencida"
