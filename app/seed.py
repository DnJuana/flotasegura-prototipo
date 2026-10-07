"""Carga de datos iniciales de prueba.

Responsable: Integrante E.

Uso:
    python -m app.seed

No hay pantallas para crear usuarios, camiones ni planes: todo se carga
desde aqui. Usar datos ficticios (nombres inventados), nunca datos reales
de personas: es un punto del criterio 5 del informe.
"""
from . import create_app
from .db import get_db, init_db


def cargar_datos(conexion) -> None:
    """Inserta los datos minimos para probar el modulo.

    TODO (E). Sugerencia de datos:
      - 1 jefe de flota y 3 conductores (contrasenas con hash_contrasena de auth.py)
      - 4 camiones: 3 asignados a un conductor y 1 sin conductor
      - por camion, 1 plan por km (aceite) y 1 plan por fecha (frenos)
      - dejar un camion cerca del umbral y otro con mantencion vencida,
        para poder mostrar los tres colores del semaforo
    """
    raise NotImplementedError("cargar_datos pendiente")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        init_db()
        cargar_datos(get_db())
        print("Datos de prueba cargados.")
