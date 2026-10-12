"""Pruebas de consulta de estado y alertas (RF4, RF9).

Responsable: Integrante E (Felipe Aravena).
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).

Datos de app/seed.py que usan estas pruebas:
    usuario 1  jefe.flota   jefe_flota
    usuario 2  conductor1   conductor   camion 1  FLSG-11  operativo
    usuario 3  conductor2   conductor   camion 2  FLSG-22  alerta_temprana
    usuario 4  conductor3   conductor   camion 3  FLSG-33  mantencion_vencida
                                        camion 4  FLSG-44  operativo, sin conductor
"""
import pytest

from app.auth import crear_token


# ---------------------------------------------------------------- utilidades
def _cabecera(usuario_id, rol):
    return {"Authorization": f"Bearer {crear_token(usuario_id, rol)}"}


def _jefe():
    return _cabecera(1, "jefe_flota")


def _conductor(usuario_id):
    return _cabecera(usuario_id, "conductor")


def _crear_alerta(conexion, camion_id, destinatario_id, nivel, mensaje):
    """Inserta una alerta directamente, usando el plan de aceite del camion."""
    plan_id = conexion.execute(
        "SELECT id FROM planes_mantencion WHERE camion_id = ? AND tipo = 'aceite'",
        (camion_id,),
    ).fetchone()[0]
    conexion.execute(
        "INSERT INTO alertas (camion_id, plan_id, destinatario_id, nivel, mensaje) "
        "VALUES (?, ?, ?, ?, ?)",
        (camion_id, plan_id, destinatario_id, nivel, mensaje),
    )
    conexion.commit()


# ------------------------------------------------------------- CP-20 y CP-21
def test_cp_20_estado_devuelve_color_del_semaforo(client, datos):
    """CP-20 | Funcional | RF4

    Entrada: GET estado de un camion en alerta temprana. Esperado: 200 con color amarillo.
    """
    respuesta = client.get("/camiones/2/estado", headers=_conductor(3))

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        "camion_id": 2,
        "patente": "FLSG-22",
        "km_actual": 148_500,
        "estado": "alerta_temprana",
        "color": "amarillo",
    }


def test_cp_21_cada_usuario_ve_solo_sus_alertas(client, datos):
    """CP-21 | Seguridad | RF9

    Entrada: GET /alertas como conductor. Esperado: solo alertas con su destinatario_id.
    """
    _crear_alerta(datos, 1, 2, "alerta_temprana", "Alerta para conductor1")
    _crear_alerta(datos, 2, 3, "mantencion_vencida", "Alerta para conductor2")
    _crear_alerta(datos, 2, 1, "mantencion_vencida", "Alerta para el jefe de flota")

    respuesta = client.get("/alertas", headers=_conductor(2))

    assert respuesta.status_code == 200
    alertas = respuesta.get_json()
    assert len(alertas) == 1
    assert alertas[0]["mensaje"] == "Alerta para conductor1"
    assert alertas[0]["camion_id"] == 1
    assert set(alertas[0]) == {"id", "camion_id", "nivel", "mensaje", "fecha"}

    # El otro conductor ve la suya y no la de conductor1.
    de_conductor2 = client.get("/alertas", headers=_conductor(3)).get_json()
    assert [a["mensaje"] for a in de_conductor2] == ["Alerta para conductor2"]

    # Un usuario sin alertas recibe una lista vacia, no un error.
    de_conductor3 = client.get("/alertas", headers=_conductor(4))
    assert de_conductor3.status_code == 200
    assert de_conductor3.get_json() == []


# ------------------------------------------------- casos adicionales (CP-35+)
@pytest.mark.parametrize(
    "camion_id, estado, color",
    [
        (1, "operativo", "verde"),
        (2, "alerta_temprana", "amarillo"),
        (3, "mantencion_vencida", "rojo"),
    ],
)
def test_cp_35_los_tres_colores_del_semaforo(client, datos, camion_id, estado, color):
    """CP-35 | Funcional | RF4

    Entrada: el jefe de flota consulta un camion en cada estado. Esperado: 200 con el color que corresponde.
    """
    respuesta = client.get(f"/camiones/{camion_id}/estado", headers=_jefe())

    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert cuerpo["estado"] == estado
    assert cuerpo["color"] == color


@pytest.mark.parametrize("camion_id", [999, 99999999999999999999])
def test_cp_36_estado_de_camion_inexistente(client, datos, camion_id):
    """CP-36 | Funcional - caso de error | RF4

    Entrada: id de camion que no existe, y un id fuera del rango de la base. Esperado: 404, sin error 500.
    """
    respuesta = client.get(f"/camiones/{camion_id}/estado", headers=_jefe())

    assert respuesta.status_code == 404


@pytest.mark.parametrize("ruta", ["/camiones/1/estado", "/alertas"])
def test_cp_37_estado_y_alertas_exigen_token(client, datos, ruta):
    """CP-37 | Seguridad | RF9

    Entrada: consulta sin cabecera Authorization, con la firma del token alterada y con el
    contenido del token cambiado a jefe_flota conservando la firma original.
    Esperado: 401 en los tres casos.
    """
    assert client.get(ruta).status_code == 401

    token = crear_token(2, "conductor")
    contenido, marca_tiempo, firma = token.split(".")

    # Firma alterada: se cambia un caracter del medio. No se usa el ultimo
    # porque en base64 sus bits finales se descartan y el token podria
    # seguir siendo el mismo.
    medio = len(firma) // 2
    otra = "A" if firma[medio] != "A" else "B"
    firma_alterada = firma[:medio] + otra + firma[medio + 1:]
    cabecera = {"Authorization": f"Bearer {contenido}.{marca_tiempo}.{firma_alterada}"}
    assert client.get(ruta, headers=cabecera).status_code == 401

    # Escalada de privilegios: contenido de jefe de flota con la firma del conductor.
    contenido_jefe = crear_token(1, "jefe_flota").split(".")[0]
    cabecera = {"Authorization": f"Bearer {contenido_jefe}.{marca_tiempo}.{firma}"}
    assert client.get(ruta, headers=cabecera).status_code == 401


def test_cp_38_conductor_no_ve_estado_de_camion_ajeno(client, datos):
    """CP-38 | Seguridad | RF9, RNF Seguridad

    Entrada: conductor1 consulta su camion, el de conductor2 y el camion sin conductor; el jefe consulta el camion sin conductor.
    Esperado: 200 en el propio, 403 en los ajenos, 200 para el jefe de flota.
    """
    assert client.get("/camiones/1/estado", headers=_conductor(2)).status_code == 200

    ajeno = client.get("/camiones/2/estado", headers=_conductor(2))
    assert ajeno.status_code == 403
    assert "patente" not in ajeno.get_json()  # el rechazo no filtra datos del camion

    assert client.get("/camiones/4/estado", headers=_conductor(2)).status_code == 403
    assert client.get("/camiones/4/estado", headers=_jefe()).status_code == 200
