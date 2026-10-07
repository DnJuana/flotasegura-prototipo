"""Prueba de humo: confirma que la aplicacion arranca. Ya esta lista."""


def test_la_api_responde(client):
    respuesta = client.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["estado"] == "ok"


def test_se_crean_las_tablas(conexion):
    tablas = {
        fila["name"]
        for fila in conexion.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert {"usuarios", "camiones", "planes_mantencion",
            "registros_kilometraje", "alertas"} <= tablas
