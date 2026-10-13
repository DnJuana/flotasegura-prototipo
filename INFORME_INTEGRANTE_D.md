# Informe Técnico - Integrante D (RF1, Criterios 7 y 8)

## Criterio 7: Evidencia de Pruebas Unitarias, Integración y Cobertura (RF1)

### 1. Resumen de Ejecución y Cobertura
El módulo `app/rutas_kilometraje.py` y sus componentes dependientes fueron validados con `pytest`, alcanzando una tasa de éxito del **100%** en la suite activa (**48 pruebas aprobadas**, 11 omitidas correspondientes a módulos secundarios).

* **Framework de pruebas:** `pytest 9.0.2` con plugin `pytest-cov`.
* **Resultado de ejecución:** `48 passed, 11 skipped in 5.70s`.
* **Estado de fallas:** 0 errores / 0 fallas.

### 2. Matriz de Casos de Prueba Evaluados (Módulo Kilometraje)

| Código | Tipo / Enfoque | Requerimiento | Entrada / Escenario | Resultado Esperado | Resultado Obtenido | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CP-14** | Funcional | RF1 | Conductor registra km válido mayor al actual. | `201 Created`, `km_actual` actualizado en BD. | `201 Created` | **PASÓ** |
| **CP-15** | Error funcional | RF1 | Registra km menor al actual del camión. | `400 Bad Request`, no modifica BD. | `400 Bad Request` | **PASÓ** |
| **CP-16** | Caso límite | RF1 | Registra km exactamente igual al actual. | `201 Created`, mantiene historial sin error. | `201 Created` | **PASÓ** |
| **CP-17** | Validación / OWASP | RF1 / OWASP A03 | Valores inválidos: negativos, decimales, `null`, SQLi (`DROP TABLE`). | `400 Bad Request` en todos los tipos de datos. | `400 Bad Request` | **PASÓ** |
| **CP-19** | Flujo Completo | RF1, RF3, RF4 | Lectura de km cruza umbral de mantenimiento. | `201 Created`, estado a `alerta_temprana` y genera alertas. | `201 Created` | **PASÓ** |
| **CP-28** | Robustez | RF1 | Petición sin cuerpo JSON, mal formado o sin clave `kilometraje`. | `400 Bad Request`, prevención de `500`. | `400 Bad Request` | **PASÓ** |
| **CP-30** | Regla Negocio | RF1, RF4 | Registro repetido en el mismo rango de alerta. | Genera notificación **solo** si cambia el estado. | `201 Created` (sin duplicar alertas) | **PASÓ** |
| **CP-31** | Seguridad / BD | RF1 (DEF-D1) | `camion_id` fuera de rango de entero SQLite (`99999999999999999999`). | `404 Not Found` controlado (evita `OverflowError 500`). | `404 Not Found` | **PASÓ** |
| **CP-32** | Seguridad RBAC | RF1, RF9 (DEF-D2) | Token JWT firmado de un `usuario_id` borrado de la BD. | `401 Unauthorized` por integridad referencial. | `401 Unauthorized` | **PASÓ** |
| **CP-33** | Disponibilidad | RF1 (DEF-D3) | Payload excesivo (> 1 MB / ataque DoS). | `413 Payload Too Large`. | `413 Payload Too Large` | **PASÓ** |
| **CP-34** | Tolerancia Fallos | RF1, RF4 (DEF-D4) | Excepción en un observador de notificación. | Registra km en BD, responde `201 Created` y tolera la falla. | `201 Created` | **PASÓ** |

---

## Criterio 8: Arquitectura, Patrones de Diseño y Justificación Técnica

### 1. Integración de Patrones de Diseño en `rutas_kilometraje.py`

El endpoint `POST /camiones/<id>/kilometraje` actúa como el orquestador principal del sistema FlotaSegura, aplicando tres patrones de diseño fundamentales:

#### A. Role-Based Access Control (RBAC) y Seguridad Puntos Finales
* **Implementación:** Mediante el decorador `@login_requerido` y la función `puede_acceder_a_camion()`.
* **Justificación:** Garantiza que un conductor solo pueda interactuar y actualizar el kilometraje de los camiones que tiene explícitamente asignados en la base de datos, mientras que el rol `jefe_flota` mantiene visibilidad global sobre la flota.

#### B. Patrón Strategy (Cálculo de Mantenimientos)
* **Implementación:** La ruta invoca `estrategias.obtener_estrategia(plan["tipo_calculo"])`.
* **Justificación:** Desacopla las reglas de cálculo de mantenimiento del controlador HTTP. Cada plan evalúa independientemente su lógica (sea por kilometraje recorrido, por intervalo de días transcurridos o un modelo mixto), devolviendo un objeto genérico `ProximaMantencion` sin que el endpoint de kilometraje conozca los detalles algorítmicos internos.

#### C. Patrón Observer (Notificaciones de Alerta)
* **Implementación:** Clase `SujetoCamion` y suscriptores `NotificadorJefeFlota` y `NotificadorConductor`.
* **Justificación:** Permite reaccionar a cambios de estado del vehículo (`alerta_temprana` o `mantencion_vencida`) mediante un mecanismo de publicación/suscripción desacoplado. Si las reglas de notificación cambian o se añaden nuevos canales en el futuro (SMS, email), la ruta de kilometraje no requiere modificación.

---

### 2. Decisiones de Diseño y Resiliencia

1. **Atomicidad en Base de Datos:** La actualización del kilometraje actual en la tabla `camiones` y la inserción en `registros_kilometraje` se ejecutan bajo un bloque transaccional (`with conexion:` en `repositorio.py`). Esto asegura que ante cualquier fallo intermedio, los datos no queden en un estado inconsistente.
2. **Aislamiento de Fallos en Notificaciones (CP-34):** Las llamadas a los observadores dentro de `rutas_kilometraje.py` están envueltas en bloques de captura de excepciones (`try/except`). Si un canal de notificación o servicio externo falla, el registro de kilometraje del usuario permanece válido y guardado correctamente en la base de datos, garantizando la alta disponibilidad de la API.
3. **Validación Defensiva (OWASP):** Se incluyó control estricto de tipos (`isinstance` explícito para evitar la coerción de booleanos en Python), restricción de tamaño del payload HTTP a 1 MB y verificación de rangos enteros antes de consultar la base de datos para prevenir excepciones no controladas (`500`).
