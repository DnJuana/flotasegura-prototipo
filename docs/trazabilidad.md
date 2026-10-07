# Trazabilidad: requerimiento → código → prueba

Responsable de mantenerla: Integrante A. Se completa a medida que avanza el código (criterios 1 y 7).

| Requerimiento (Ev. 2) | Función del prototipo | Archivo y clase o función | Casos de prueba |
|---|---|---|---|
| RF1 — Registrar kilometraje | `POST /camiones/<id>/kilometraje` | `app/rutas_kilometraje.py` → `registrar_kilometraje`, `validar_kilometraje` | CP-14 a CP-19 |
| RF3 — Calcular próxima mantención | Motor de cálculo (Strategy) | `app/estrategias.py` → `CalculoPorKm`, `CalculoPorFecha` | CP-01 a CP-05 |
| RF4 — Alertas automáticas | Servicio de alertas (Observer) y consulta | `app/alertas.py` → `SujetoCamion`, notificadores; `app/rutas_estado.py` | CP-06 a CP-09, CP-19, CP-20 |
| RF9 — Inicio de sesión y roles | Login y control de acceso | `app/auth.py` → `login`; `app/permisos.py` → `login_requerido`, `rol_requerido` | CP-10 a CP-13, CP-21 a CP-26 |
| RNF Seguridad — hash, RBAC | Hash de contraseñas, regla de camión asignado | `app/auth.py` → `hash_contrasena`; `app/permisos.py` → `puede_acceder_a_camion` | CP-13, CP-23 a CP-25 |

## Requerimientos fuera del prototipo

RF2 (offline), RF5 (dashboard), RF6 (reportes), RF7 (gestión de planes) y RF8 (registro de mantenciones y fallas) no se implementan. Los planes de mantención se cargan desde `app/seed.py`.
