"""Punto de entrada para levantar la API en modo desarrollo.

Uso:
    python run.py
"""
from app import create_app
from app.db import init_db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        init_db()  # crea las tablas si no existen
    app.run(debug=False, port=5000)
