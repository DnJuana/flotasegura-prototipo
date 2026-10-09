"""Pruebas del patron Observer (RF4).

Responsable: Integrante B.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).
Quitar el pytest.skip al implementarla.
"""
import pytest
from app.alertas import SujetoCamion, NotificadorJefeFlota, NotificadorConductor, peor_estado
from app.estrategias import ProximaMantencion


def test_cp_06_al_cruzar_umbral_se_alerta_a_jefe_y_conductor(conexion):
    """CP-06 | Funcional | RF4
    cursor = conexion.cursor()
    cursor.execute("INSERT OR IGNORE INTO usuarios (id, nombre_usuario, nombre_completo, hash_contrasena, rol) VALUES (1, 'jefe', 'Jefe Flota', 'hash', 'jefe_flota')")
    cursor.execute("INSERT OR IGNORE INTO usuarios (id, nombre_usuario, nombre_completo, hash_contrasena, rol) VALUES (10, 'conductor1', 'Juan Perez', 'hash', 'conductor')")
    cursor.execute("INSERT OR IGNORE INTO camiones (id, patente, km_actual, estado, conductor_id) VALUES (1, 'ABCD-12', 5000, 'operativo', 10)")
    cursor.execute("INSERT OR IGNORE INTO planes_mantencion (id, camion_id, tipo, tipo_calculo) VALUES (1, 1, 'aceite', 'km')")
    conexion.commit()

    Entrada: notificar() con los dos notificadores suscritos. Esperado: una alerta para el jefe de flota y otra para el conductor.
    """
    
    camion = {"id":1,"patente": "ABCD-12", "conductor_id": 10}
    sujeto = SujetoCamion(camion)
    
    #suscribimos ambos observadores
    sujeto.suscribir(NotificadorJefeFlota(conexion))
    sujeto.suscribir(NotificadorConductor(conexion))
    
    proxima= ProximaMantencion(plan_id = 1, tipo = "aceite", estado="alerta_temprana", km_restantes=500)
    sujeto.notificar(proxima)
    
    #verificamos que se hayan guardado las alertas en la BD
    cursor= conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM alertas WHERE camion_id = ?", (1,))
    total_alertas = cursor.fetchone()[0]
    
    assert total_alertas == 2


def test_cp_07_camion_sin_conductor_solo_alerta_al_jefe(conexion):
    """CP-07 | Funcional - caso limite | RF4

    Entrada: camion con conductor_id nulo. Esperado: solo se crea la alerta del jefe de flota, sin error.
    """
    cursor = conexion.cursor()
    cursor.execute("INSERT OR IGNORE INTO usuarios (id, nombre_usuario, nombre_completo, hash_contrasena, rol) VALUES (1, 'jefe', 'Jefe Flota', 'hash', 'jefe_flota')")
    cursor.execute("INSERT OR IGNORE INTO camiones (id, patente, km_actual, estado, conductor_id) VALUES (2, 'XYZ-99', 8000, 'operativo', NULL)")
    cursor.execute("INSERT OR IGNORE INTO planes_mantencion (id, camion_id, tipo, tipo_calculo) VALUES (2, 2, 'frenos', 'km')")
    conexion.commit()
    
    camion = {"id": 2, "patente": "XYZ-99", "conductor_id": None}
    sujeto= SujetoCamion(camion)
    
    sujeto.suscribir(NotificadorJefeFlota(conexion))
    sujeto.suscribir(NotificadorConductor(conexion))
     
    proxima = ProximaMantencion(plan_id=2, tipo="frenos", estado="mantencion_vencida", km_restantes =-100)
    sujeto.notificar(proxima)
    
    #solo debe de existir 1 alerta (la del jefe de flota, ya que no hay conductores)
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM alertas WHERE camion_id =? ",(2,))
    total_alertas = cursor.fetchone()[0]
    
    assert total_alertas == 1


def test_cp_08_observador_desuscrito_no_recibe_alerta(conexion):
    """CP-08 | Funcional | RF4

    Entrada: suscribir, desuscribir y notificar. Esperado: cero alertas para ese observador.
    """
    cursor = conexion.cursor()
    cursor.execute("INSERT OR IGNORE INTO usuarios (id, nombre_usuario, nombre_completo, hash_contrasena, rol) VALUES (1, 'jefe', 'Jefe Flota', 'hash', 'jefe_flota')")
    cursor.execute("INSERT OR IGNORE INTO usuarios (id, nombre_usuario, nombre_completo, hash_contrasena, rol) VALUES (5, 'conductor2', 'Pedro', 'hash', 'conductor')")
    cursor.execute("INSERT OR IGNORE INTO camiones (id, patente, km_actual, estado, conductor_id) VALUES (3, 'TEST-03', 2000, 'operativo', 5)")
    cursor.execute("INSERT OR IGNORE INTO planes_mantencion (id, camion_id, tipo, tipo_calculo) VALUES (3, 3, 'neumaticos', 'km')")
    conexion.commit()
    
    camion = {"id": 3, "patente": "TEST-03", "conductor_id": 5}
    sujeto= SujetoCamion(camion)
    
    observador = NotificadorJefeFlota(conexion)
    sujeto.suscribir(observador)
    sujeto.desuscribir(observador)
    
    proxima = ProximaMantencion(plan_id =3, tipo="neumaticos", estado="alerta_temprana", km_restantes = 200)
    sujeto.notificar(proxima)
    
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM alertas WHERE camion_id = ?",(3,))
    total_alertas = cursor.fetchone()[0]
    
    assert total_alertas == 0


def test_cp_09_peor_estado_entre_varios_planes():
    """CP-09 | Funcional | RF4

    Entrada: un plan operativo y otro vencido. Esperado: mantencion_vencida.
    """
    planes=[
        ProximaMantencion(plan_id=1, tipo="aceite", estado="operativo", km_restantes=5000),
        ProximaMantencion(plan_id=2, tipo="frenos", estado="mantencion_vencida", km_restantes=-10)
    ]
    
    resultado= peor_estado(planes)
    assert resultado == "mantencion_vencida"
