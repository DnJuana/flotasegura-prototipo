# FlotaSegura — prototipo del módulo crítico

Prototipo de la Evaluación 3 (UA3), Grupo 5. Continúa el sistema diseñado en la Evaluación 2 para la empresa de transporte de carga FlotaSegura.

## Qué hace

Módulo de **registro de kilometraje, cálculo de próxima mantención y alertas**. Es una API REST con tres operaciones:

| Operación | Endpoint | Requerimiento (Ev. 2) |
|---|---|---|
| Iniciar sesión | `POST /login` | RF9 |
| Registrar kilometraje | `POST /camiones/<id>/kilometraje` | RF1, RF3, RF4 |
| Consultar estado y alertas | `GET /camiones/<id>/estado`, `GET /alertas` | RF4 |

## Alcance del prototipo

Se construye solo el módulo crítico. Respecto del diseño de la Evaluación 2:

- Se implementan dos estrategias de cálculo (por kilometraje y por fecha). `CalculoPorRuta` queda fuera.
- Las alertas se guardan en la base de datos; no se envían por push ni correo.
- La base de datos es SQLite en lugar de PostgreSQL.
- Hay dos roles: conductor y jefe de flota. El gerente queda fuera porque su función son los reportes.
- Quedan fuera el modo offline, el dashboard, los reportes y el registro de mantenciones y fallas.

## Patrones de diseño

| Patrón | Archivo | Clases |
|---|---|---|
| Strategy | `app/estrategias.py` | `EstrategiaCalculo`, `CalculoPorKm`, `CalculoPorFecha` |
| Observer | `app/alertas.py` | `SujetoCamion`, `ObservadorMantencion`, `NotificadorJefeFlota`, `NotificadorConductor` |

## Estructura

```
flotasegura-prototipo/
├── run.py                    Levanta la API
├── requirements.txt
├── app/
│   ├── __init__.py           Fábrica de la aplicación
│   ├── config.py             Configuración
│   ├── db.py                 Conexión a SQLite
│   ├── schema.sql            Tablas
│   ├── estrategias.py        Patrón Strategy (RF3)
│   ├── alertas.py            Patrón Observer (RF4)
│   ├── auth.py               Login, hash y token (RF9)
│   ├── permisos.py           Control de acceso por rol (RF9)
│   ├── rutas_kilometraje.py  Registro de kilometraje (RF1)
│   ├── rutas_estado.py       Estado del camión y alertas (RF4)
│   ├── repositorio.py        Consultas SQL
│   └── seed.py               Datos de prueba
├── tests/                    Pruebas con pytest (una por caso del plan)
├── docs/
│   ├── plan_pruebas.md       Plan y resultados de las pruebas
│   ├── bitacora_defectos.md  Defectos encontrados y correcciones
│   ├── trazabilidad.md       Requerimiento → código → prueba
│   └── evidencias/           Capturas
└── .github/workflows/        Ejecución automática de las pruebas
```

## Cómo ejecutarlo

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt

python -m app.seed              # carga los datos de prueba
python run.py                   # API en http://localhost:5000
```

Comprobación rápida: abrir `http://localhost:5000/salud`.

## Cómo ejecutar las pruebas

```bash
pytest -v
```

## Integrantes

Ver `REPARTO.md`.
