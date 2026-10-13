"""Pruebas del registro de kilometraje (RF1).

Responsable: Integrante D.
Cada prueba lleva el ID del plan de pruebas (docs/plan_pruebas.md).

Datos de app/seed.py que usan estas pruebas:
    camion 1  FLSG-11  km 100.000  operativo           conductor1 (usuario 2)
    camion 2  FLSG-22  km 148.500  alerta_temprana     conductor2 (usuario 3)
    camion 3  FLSG-33  km 210.300  mantencion_vencida  conductor3 (usuario 4)
    camion 4  FLSG-44  km  50.000  operativo           sin conductor
    plan de aceite del camion 1: limite 105.000 km, aviso 1.000 km antes.
    usuario 1 = jefe de flota.
"""
import pytest

from app.auth import crear_token

KM_MAXIMO = 2_000_000


# ---------------------------------------------------------------- utilidades
def _cabecera(usuario_id, rol):
    return {"Authorization": f"Bearer {crear_token(usuario_id, rol)}"}


def _conductor1():
    return _cabecera(2, "conductor")


def _jefe():
    return _cabecera(1, "jefe_flota")


def _km_actual(conexion, camion_id):
    return conexion.execute(
        "SELECT km_actual FROM camiones WHERE id = ?", (camion_id,)
    ).fetchone()[0]


def _estado(conexion, camion_id):
    return conexion.execute(
        "SELECT estado FROM camiones WHERE id = ?", (camion_id,)
    ).fetchone()[0]


def _n_registros(conexion, camion_id):
    return conexion.execute(
        "SELECT COUNT(*) FROM registros_kilometraje WHERE camion_id = ?", (camion_id,)
    ).fetchone()[0]


def _n_alertas(conexion, camion_id):
    return conexion.execute(
        "SELECT COUNT(*) FROM alertas WHERE camion_id = ?", (camion_id,)
    ).fetchone()[0]


# ------------------------------------------------------------- CP-14 a CP-19
def test_cp_14_registro_valido(client, datos):
    """CP-14 | Funcional | RF1

    Entrada: conductor registra un km mayor al actual en su camion. Esperado: 201 y km_actual actualizado.
    """
    r = client.post("/camiones/1/kilometraje", json={"kilometraje": 101_000},
                    headers=_conductor1())

    assert r.status_code == 201
    cuerpo = r.get_json()
    assert cuerpo["camion_id"] == 1
    assert cuerpo["km_actual"] == 101_000
    assert cuerpo["estado"] == "operativo"
    assert _km_actual(datos, 1) == 101_000
    assert _n_registros(datos, 1) == 1


def test_cp_15_km_menor_al_actual(client, datos):
    """CP-15 | Funcional - caso de error | RF1

    Entrada: km inferior al ultimo registrado. Esperado: 400 y km_actual sin cambios.
    """
    r = client.post("/camiones/1/kilometraje", json={"kilometraje": 99_999},
                    headers=_conductor1())

    assert r.status_code == 400
    assert _km_actual(datos, 1) == 100_000
    assert _n_registros(datos, 1) == 0


def test_cp_16_km_igual_al_actual(client, datos):
    """CP-16 | Funcional - caso limite | RF1

    Entrada: km identico al actual.
    REGLA DOCUMENTADA: se ACEPTA (201). La regla de negocio dice "no puede ser
    menor al actual"; un camion detenido puede informar el mismo km y queda
    en el historial. El km_actual no cambia.
    """
    r = client.post("/camiones/1/kilometraje", json={"kilometraje": 100_000},
                    headers=_conductor1())

    assert r.status_code == 201
    assert r.get_json()["km_actual"] == 100_000
    assert _km_actual(datos, 1) == 100_000
    assert _n_registros(datos, 1) == 1


@pytest.mark.parametrize("valor", [-5, "abc", 1500.5, None, True, "150000", [150000], {"km": 1},
                                   "1; DROP TABLE camiones;--"])
def test_cp_17_km_negativo_o_no_numerico(client, datos, valor):
    """CP-17 | Funcional - caso de error | RF1

    Entrada: -5, 'abc', 1500.5, null (y ademas true, '150000', lista, objeto y
    un texto con inyeccion SQL). OWASP A03.
    Esperado: 400 en todos los casos y nada guardado.
    """
    r = client.post("/camiones/1/kilometraje", json={"kilometraje": valor},
                    headers=_conductor1())

    assert r.status_code == 400
    assert _km_actual(datos, 1) == 100_000
    assert _n_registros(datos, 1) == 0


def test_cp_18_camion_inexistente(client, datos):
    """CP-18 | Funcional - caso de error | RF1

    Entrada: id de camion que no existe. Esperado: 404.
    """
    r = client.post("/camiones/999/kilometraje", json={"kilometraje": 150_000},
                    headers=_jefe())

    assert r.status_code == 404


def test_cp_19_registro_que_cruza_el_umbral_genera_alerta(client, datos):
    """CP-19 | Funcional - flujo completo | RF1, RF3, RF4

    Entrada: km que deja al camion dentro del umbral (104.200: faltan 800 km
    para el limite 105.000 y el aviso es a 1.000 km).
    Esperado: estado alerta_temprana y alertas creadas (jefe + conductor).
    """
    r = client.post("/camiones/1/kilometraje", json={"kilometraje": 104_200},
                    headers=_conductor1())

    assert r.status_code == 201
    cuerpo = r.get_json()
    assert cuerpo["estado"] == "alerta_temprana"
    aceite = [p for p in cuerpo["proximas_mantenciones"] if p["tipo"] == "aceite"][0]
    assert aceite["km_restantes"] == 800
    assert _estado(datos, 1) == "alerta_temprana"

    destinatarios = {f[0] for f in datos.execute(
        "SELECT destinatario_id FROM alertas WHERE camion_id = 1")}
    assert destinatarios == {1, 2}          # jefe de flota y conductor del camion


# ------------------------------------------- casos adicionales de este modulo
def test_cp_27_km_sobre_el_maximo(client, datos):
    """CP-27 | Seguridad / validacion - caso limite | RF1

    Entrada: KM_MAXIMO exacto (se acepta) y KM_MAXIMO + 1 (se rechaza).
    """
    r_ok = client.post("/camiones/1/kilometraje", json={"kilometraje": KM_MAXIMO},
                       headers=_jefe())
    assert r_ok.status_code == 201

    r_mal = client.post("/camiones/1/kilometraje", json={"kilometraje": KM_MAXIMO + 1},
                        headers=_jefe())
    assert r_mal.status_code == 400
    assert _km_actual(datos, 1) == KM_MAXIMO


def test_cp_28_cuerpo_ausente_o_mal_formado(client, datos):
    """CP-28 | Seguridad / validacion - caso de error | RF1

    Entrada: sin cuerpo, JSON roto, JSON que no es objeto, objeto sin la clave
    'kilometraje'. Esperado: 400 (nunca 500).
    """
    h = _conductor1()
    casos = [
        {"data": None},                                               # sin cuerpo
        {"data": "{no es json", "content_type": "application/json"},  # JSON roto
        {"json": [100500]},                                           # JSON sin objeto
        {"json": {"otra_clave": 100500}},                             # falta la clave
        {"json": {}},
    ]
    for kwargs in casos:
        r = client.post("/camiones/1/kilometraje", headers=h, **kwargs)
        assert r.status_code == 400, kwargs
    assert _km_actual(datos, 1) == 100_000


def test_cp_29_jefe_de_flota_registra_en_cualquier_camion(client, datos):
    """CP-29 | Funcional / control de acceso | RF1, RF9

    Entrada: el jefe de flota registra km en un camion sin conductor (camion 4).
    Esperado: 201; el registro queda a nombre del jefe.
    """
    r = client.post("/camiones/4/kilometraje", json={"kilometraje": 51_000},
                    headers=_jefe())

    assert r.status_code == 201
    assert _km_actual(datos, 4) == 51_000
    dueno = datos.execute(
        "SELECT conductor_id FROM registros_kilometraje WHERE camion_id = 4").fetchone()[0]
    assert dueno == 1


def test_cp_30_alertas_solo_cuando_cambia_el_estado(client, datos):
    """CP-30 | Funcional - flujo completo | RF1, RF4

    Camion 2 ya esta en alerta_temprana (faltan 500 km).
      a) 148.600 -> sigue en alerta_temprana: NO se generan alertas nuevas.
      b) 150.000 -> pasa a mantencion_vencida: SI se generan alertas.
    """
    h = _cabecera(3, "conductor")

    r = client.post("/camiones/2/kilometraje", json={"kilometraje": 148_600}, headers=h)
    assert r.status_code == 201
    assert r.get_json()["estado"] == "alerta_temprana"
    assert _n_alertas(datos, 2) == 0

    r = client.post("/camiones/2/kilometraje", json={"kilometraje": 150_000}, headers=h)
    assert r.status_code == 201
    assert r.get_json()["estado"] == "mantencion_vencida"
    assert _estado(datos, 2) == "mantencion_vencida"
    assert _n_alertas(datos, 2) >= 2


# ---------------- casos nacidos de pruebas exploratorias (defectos DEF-D1..D4)
def _sin_propagar(app):
    """Hace que un error interno se vea como respuesta 500 (como en produccion)
    en vez de relanzarse dentro de la prueba."""
    app.config["PROPAGATE_EXCEPTIONS"] = False


def test_cp_31_id_de_camion_gigante(app, client, datos):
    """CP-31 | Seguridad - validacion de entrada | RF1 (DEF-D1)

    Entrada: /camiones/99999999999999999999/kilometraje (no cabe en un INTEGER de SQLite).
    Esperado: 404, nunca 500.
    """
    _sin_propagar(app)
    r = client.post("/camiones/99999999999999999999/kilometraje",
                    json={"kilometraje": 1}, headers=_jefe())

    assert r.status_code == 404


def test_cp_32_token_firmado_de_usuario_inexistente(app, client, datos):
    """CP-32 | Seguridad - autenticacion | RF1, RF9 (DEF-D2)

    Entrada: token valido (bien firmado) cuyo usuario_id ya no existe en la base.
    Esperado: 401 y ningun registro guardado, nunca 500.
    """
    _sin_propagar(app)
    r = client.post("/camiones/1/kilometraje", json={"kilometraje": 120_000},
                    headers=_cabecera(999, "jefe_flota"))

    assert r.status_code == 401
    assert _km_actual(datos, 1) == 100_000
    assert _n_registros(datos, 1) == 0


def test_cp_33_cuerpo_demasiado_grande(client, datos):
    """CP-33 | Seguridad - disponibilidad | RF1 (DEF-D3)

    Entrada: JSON de 5 MB con un kilometraje valido y relleno. Esperado: 413 y nada guardado.
    """
    cuerpo = '{"kilometraje": 120000, "relleno": "' + "A" * 5_000_000 + '"}'
    r = client.post("/camiones/1/kilometraje", data=cuerpo,
                    content_type="application/json", headers=_jefe())

    assert r.status_code == 413
    assert _km_actual(datos, 1) == 100_000


def test_cp_34_falla_un_notificador_no_deja_datos_incoherentes(app, client, datos, monkeypatch):
    """CP-34 | Funcional - tolerancia a fallos | RF1, RF4 (DEF-D4)

    Entrada: el registro cruza el umbral pero un observador lanza una excepcion.
    Esperado: el km y el estado del camion quedan coherentes (km nuevo y
    alerta_temprana) y el conductor recibe 201.
    """
    _sin_propagar(app)
    from app import alertas

    def roto(self, camion, proxima):
        raise RuntimeError("falla simulada del notificador")

    monkeypatch.setattr(alertas.NotificadorConductor, "actualizar", roto)

    r = client.post("/camiones/1/kilometraje", json={"kilometraje": 104_200},
                    headers=_conductor1())

    assert r.status_code == 201
    assert _km_actual(datos, 1) == 104_200
    assert _estado(datos, 1) == "alerta_temprana"
