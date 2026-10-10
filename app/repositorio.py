"""Acceso a datos: todas las consultas SQL del prototipo.

Responsable: Integrante E (Felipe Aravena).

Reglas de este archivo:
  - Las consultas siempre usan parametros (?). Nunca se arma el SQL
    concatenando texto que viene del usuario (previene inyeccion SQL).
  - Las funciones de lectura devuelven dict (o None si no hay fila), no
    sqlite3.Row, porque el resto del codigo usa camion.get("conductor_id")
    y eso solo existe en dict.
"""
from .db import get_db


def _a_dict(fila):
    """Convierte una fila de SQLite en dict. None se mantiene como None."""
    return dict(fila) if fila is not None else None


def buscar_usuario_por_nombre(nombre_usuario: str):
    """Devuelve el usuario (dict) o None si no existe. La usa el login."""
    fila = get_db().execute(
        "SELECT id, nombre_usuario, nombre_completo, hash_contrasena, rol "
        "FROM usuarios WHERE nombre_usuario = ?",
        (nombre_usuario,),
    ).fetchone()
    return _a_dict(fila)


def buscar_camion(camion_id: int):
    """Devuelve el camion (dict) o None si no existe."""
    fila = get_db().execute(
        "SELECT id, patente, km_actual, estado, conductor_id "
        "FROM camiones WHERE id = ?",
        (camion_id,),
    ).fetchone()
    return _a_dict(fila)


def planes_de_camion(camion_id: int) -> list:
    """Devuelve los planes de mantencion del camion como lista de dict.

    Un camion sin planes devuelve una lista vacia.
    """
    filas = get_db().execute(
        "SELECT id, camion_id, tipo, tipo_calculo, "
        "       intervalo_km, km_ultima_mantencion, umbral_aviso_km, "
        "       intervalo_dias, fecha_ultima_mantencion, umbral_aviso_dias "
        "FROM planes_mantencion WHERE camion_id = ? ORDER BY id",
        (camion_id,),
    ).fetchall()
    return [dict(fila) for fila in filas]


def guardar_registro_kilometraje(camion_id: int, conductor_id: int, kilometraje: int) -> int:
    """Inserta el registro y actualiza km_actual del camion.

    Las dos operaciones van en una misma transaccion: si una falla, no se
    guarda ninguna (el bloque "with" hace commit al terminar bien y
    rollback si hay un error). Devuelve el id del registro creado.
    """
    conexion = get_db()
    with conexion:
        cursor = conexion.execute(
            "INSERT INTO registros_kilometraje (camion_id, conductor_id, kilometraje) "
            "VALUES (?, ?, ?)",
            (camion_id, conductor_id, kilometraje),
        )
        conexion.execute(
            "UPDATE camiones SET km_actual = ? WHERE id = ?",
            (kilometraje, camion_id),
        )
    return cursor.lastrowid


def actualizar_estado_camion(camion_id: int, estado: str) -> None:
    """Guarda el nuevo estado del camion.

    Los valores validos los controla la base de datos (CHECK en schema.sql):
    operativo, alerta_temprana o mantencion_vencida.
    """
    conexion = get_db()
    with conexion:
        conexion.execute(
            "UPDATE camiones SET estado = ? WHERE id = ?",
            (estado, camion_id),
        )


def alertas_de_usuario(usuario_id: int) -> list:
    """Alertas dirigidas al usuario, de la mas reciente a la mas antigua."""
    filas = get_db().execute(
        "SELECT id, camion_id, plan_id, nivel, mensaje, fecha "
        "FROM alertas WHERE destinatario_id = ? "
        "ORDER BY fecha DESC, id DESC",
        (usuario_id,),
    ).fetchall()
    return [dict(fila) for fila in filas]
