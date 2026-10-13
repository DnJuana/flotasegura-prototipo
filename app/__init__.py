"""FlotaSegura - prototipo del modulo critico.

Modulo: registro de kilometraje, calculo de proxima mantencion y alertas.
Requerimientos de la Evaluacion 2 que cubre: RF1, RF3, RF4 y RF9.
"""
from flask import Flask, jsonify

from . import db
from .config import Config


def create_app(config_extra=None):
    """Fabrica de la aplicacion. Los tests la llaman con una base temporal."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if config_extra:
        app.config.update(config_extra)

    db.registrar(app)

    # Cada integrante registra aqui su blueprint cuando lo tenga listo.
    from .auth import bp as auth_bp
    from .rutas_estado import bp as estado_bp
    from .rutas_kilometraje import bp as kilometraje_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(kilometraje_bp)
    app.register_blueprint(estado_bp)

    @app.get("/salud")
    def salud():
        return jsonify(estado="ok", servicio="flotasegura-prototipo")

    return app
