"""Carga de datos iniciales de prueba.

Responsable: Integrante E (Felipe Aravena).

Uso:
    python -m app.seed

No hay pantallas para crear usuarios, camiones ni planes: todo se carga
desde aqui. Todos los datos son ficticios (nombres y patentes inventados);
el prototipo no usa datos reales de personas.

Los cuatro camiones cubren los casos que necesitan las pruebas:

    id  patente   conductor      estado inicial       para que sirve
    1   FLSG-11   conductor1     operativo            camino normal
    2   FLSG-22   conductor2     alerta_temprana      semaforo amarillo
    3   FLSG-33   conductor3     mantencion_vencida   semaforo rojo
    4   FLSG-44   (sin asignar)  operativo            caso limite sin conductor

El jefe de flota se inserta primero para que quede con id 1.
"""
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from . import create_app
from .db import get_db, init_db

# Contrasena unica para todos los usuarios de prueba. Solo sirve en la
# base local de desarrollo; no es una credencial real.
CONTRASENA_PRUEBA = "FlotaSegura.2026"

# (id, nombre_usuario, nombre_completo, rol)
USUARIOS = [
    (1, "jefe.flota", "Marta Rojas Fuentes", "jefe_flota"),
    (2, "conductor1", "Luis Soto Vera", "conductor"),
    (3, "conductor2", "Camilo Paredes Lagos", "conductor"),
    (4, "conductor3", "Rosa Mella Tapia", "conductor"),
]

# (id, patente, km_actual, estado, conductor_id)
CAMIONES = [
    (1, "FLSG-11", 100_000, "operativo", 2),
    (2, "FLSG-22", 148_500, "alerta_temprana", 3),
    (3, "FLSG-33", 210_300, "mantencion_vencida", 4),
    (4, "FLSG-44", 50_000, "operativo", None),
]

# Plan de aceite por kilometraje: cada 10.000 km, aviso 1.000 km antes.
# (camion_id, km_ultima_mantencion) -> km restantes con el km_actual de arriba
PLANES_KM = [
    (1, 95_000),   # limite 105.000 -> faltan 5.000  (operativo)
    (2, 139_000),  # limite 149.000 -> faltan 500    (alerta temprana)
    (3, 200_000),  # limite 210.000 -> pasado en 300 (vencida)
    (4, 45_000),   # limite 55.000  -> faltan 5.000  (operativo)
]
INTERVALO_KM = 10_000
UMBRAL_AVISO_KM = 1_000

# Plan de frenos por fecha: cada 180 dias, aviso 15 dias antes.
# La ultima revision de todos fue hace 30 dias, asi que quedan 150 dias.
INTERVALO_DIAS = 180
UMBRAL_AVISO_DIAS = 15
DIAS_DESDE_ULTIMA_REVISION = 30


def cargar_datos(conexion, hoy=None) -> bool:
    """Inserta los datos de prueba.

    Si la base ya tiene usuarios no hace nada, para poder ejecutar el
    script mas de una vez sin duplicar ni romper datos. Devuelve True si
    cargo los datos y False si ya existian.

    hoy: fecha de referencia para los planes por fecha. Por defecto es la
    fecha actual; las pruebas pueden pasar una fecha fija.
    """
    ya_hay_datos = conexion.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] > 0
    if ya_hay_datos:
        return False

    hoy = hoy or date.today()
    ultima_revision = (hoy - timedelta(days=DIAS_DESDE_ULTIMA_REVISION)).isoformat()
    # El hash se calcula una vez y se reutiliza: todos comparten la contrasena.
    hash_prueba = generate_password_hash(CONTRASENA_PRUEBA)

    with conexion:  # una sola transaccion: se carga todo o nada
        conexion.executemany(
            "INSERT INTO usuarios (id, nombre_usuario, nombre_completo, hash_contrasena, rol) "
            "VALUES (?, ?, ?, ?, ?)",
            [(uid, usuario, nombre, hash_prueba, rol) for uid, usuario, nombre, rol in USUARIOS],
        )
        conexion.executemany(
            "INSERT INTO camiones (id, patente, km_actual, estado, conductor_id) "
            "VALUES (?, ?, ?, ?, ?)",
            CAMIONES,
        )
        conexion.executemany(
            "INSERT INTO planes_mantencion "
            "(camion_id, tipo, tipo_calculo, intervalo_km, km_ultima_mantencion, umbral_aviso_km) "
            "VALUES (?, 'aceite', 'km', ?, ?, ?)",
            [(camion_id, INTERVALO_KM, km_ultima, UMBRAL_AVISO_KM) for camion_id, km_ultima in PLANES_KM],
        )
        conexion.executemany(
            "INSERT INTO planes_mantencion "
            "(camion_id, tipo, tipo_calculo, intervalo_dias, fecha_ultima_mantencion, umbral_aviso_dias) "
            "VALUES (?, 'frenos', 'fecha', ?, ?, ?)",
            [(camion[0], INTERVALO_DIAS, ultima_revision, UMBRAL_AVISO_DIAS) for camion in CAMIONES],
        )
    return True


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        init_db()
        if cargar_datos(get_db()):
            print("Datos de prueba cargados: 4 usuarios, 4 camiones y 8 planes.")
        else:
            print("La base ya tenia datos; no se cargo nada.")
