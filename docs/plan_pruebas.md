# Plan de pruebas

Responsable de mantenerlo: Integrante D. Cada integrante completa las filas de sus casos.

Las columnas **Resultado obtenido**, **Estado** y **Evidencia** se llenan solo después de ejecutar la prueba de verdad. El docente puede reproducir cualquier caso: si el resultado no coincide con lo informado, el criterio 7 queda en No logrado.

Estado: `Pasa`, `Falla` (anotar el defecto en la bitácora) o `Pendiente`.

| ID | Objetivo | Tipo | Requerimiento | Entrada | Resultado esperado | Resultado obtenido | Estado | Evidencia | Archivo |
|---|---|---|---|---|---|---|---|---|---|
| CP-01 | Km lejos del umbral | Funcional | RF3 | plan cada 10.000 km, faltan 5.000 | estado operativo y km_restantes = 5000 |  | Pendiente |  | `tests/test_estrategias.py` |
| CP-02 | Km justo en el umbral | Funcional - caso limite | RF3 | km_restantes igual al umbral de aviso | alerta_temprana |  | Pendiente |  | `tests/test_estrategias.py` |
| CP-03 | Km sobrepasado | Funcional | RF3 | km_actual supera el limite del plan | mantencion_vencida y km_restantes <= 0 |  | Pendiente |  | `tests/test_estrategias.py` |
| CP-04 | Fecha vencida | Funcional | RF3 | plan por fecha con la fecha limite ya pasada | mantencion_vencida |  | Pendiente |  | `tests/test_estrategias.py` |
| CP-05 | Tipo de calculo desconocido | Funcional - caso de error | RF3 | obtener_estrategia('ruta') | ValueError |  | Pendiente |  | `tests/test_estrategias.py` |
| CP-06 | Al cruzar umbral se alerta a jefe y conductor | Funcional | RF4 | notificar() con los dos notificadores suscritos | una alerta para el jefe de flota y otra para el conductor |  | Pendiente |  | `tests/test_alertas.py` |
| CP-07 | Camion sin conductor solo alerta al jefe | Funcional - caso limite | RF4 | camion con conductor_id nulo | solo se crea la alerta del jefe de flota, sin error |  | Pendiente |  | `tests/test_alertas.py` |
| CP-08 | Observador desuscrito no recibe alerta | Funcional | RF4 | suscribir, desuscribir y notificar | cero alertas para ese observador |  | Pendiente |  | `tests/test_alertas.py` |
| CP-09 | Peor estado entre varios planes | Funcional | RF4 | un plan operativo y otro vencido | mantencion_vencida |  | Pendiente |  | `tests/test_alertas.py` |
| CP-10 | Login correcto entrega token | Funcional | RF9 | usuario y contrasena validos | 200 con token y rol |  | Pendiente |  | `tests/test_auth.py` |
| CP-11 | Contrasena incorrecta | Seguridad - caso de error | RF9 | usuario valido con contrasena erronea | 401, mismo mensaje que para usuario inexistente |  | Pendiente |  | `tests/test_auth.py` |
| CP-12 | Login sin campos | Funcional - caso de error | RF9 | cuerpo vacio o sin contrasena | 400 |  | Pendiente |  | `tests/test_auth.py` |
| CP-13 | La contrasena se guarda con hash | Seguridad | RNF Seguridad | leer hash_contrasena de la base | no contiene la contrasena en texto plano |  | Pendiente |  | `tests/test_auth.py` |
| CP-14 | Registro valido | Funcional | RF1 | conductor registra un km mayor al actual en su camion | 201 y km_actual actualizado |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-15 | Km menor al actual | Funcional - caso de error | RF1 | km inferior al ultimo registrado | 400 y km_actual sin cambios |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-16 | Km igual al actual | Funcional - caso limite | RF1 | km identico al actual | definir y documentar la regla (aceptar o rechazar) |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-17 | Km negativo o no numerico | Funcional - caso de error | RF1 | -5, 'abc', 1500.5, null | 400 en todos los casos |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-18 | Camion inexistente | Funcional - caso de error | RF1 | id de camion que no existe | 404 |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-19 | Registro que cruza el umbral genera alerta | Funcional - flujo completo | RF1, RF3, RF4 | km que deja al camion dentro del umbral | estado alerta_temprana y alertas creadas |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-20 | Estado devuelve color del semaforo | Funcional | RF4 | GET estado de un camion en alerta temprana | 200 con color amarillo |  | Pendiente |  | `tests/test_estado.py` |
| CP-21 | Cada usuario ve solo sus alertas | Seguridad | RF9 | GET /alertas como conductor | solo alertas con su destinatario_id |  | Pendiente |  | `tests/test_estado.py` |
| CP-22 | Sin token se rechaza | Seguridad | RF9 | POST kilometraje sin cabecera Authorization | 401 |  | Pendiente |  | `tests/test_seguridad.py` |
| CP-23 | Conductor no registra en camion ajeno | Seguridad | RF9 | conductor A registra km en el camion de B | 403 y ningun registro guardado |  | Pendiente |  | `tests/test_seguridad.py` |
| CP-24 | Conductor no ve estado de camion ajeno | Seguridad | RF9 | conductor A consulta el estado del camion de B | 403 |  | Pendiente |  | `tests/test_seguridad.py` |
| CP-25 | Inyeccion sql en login | Seguridad | RNF Seguridad | usuario = " ' OR '1'='1 " | 401, sin error 500 |  | Pendiente |  | `tests/test_seguridad.py` |
| CP-26 | Token alterado o expirado | Seguridad | RF9 | token con un caracter cambiado, y token vencido | 401 en ambos |  | Pendiente |  | `tests/test_seguridad.py` |

## Cómo dejar evidencia

- Ejecutar `pytest -v` y guardar la captura de la terminal en `docs/evidencias/` con el ID del caso en el nombre (ejemplo: `CP-15_falla.png`, `CP-15_pasa.png`).
- Para los endpoints, sumar una captura de la petición y la respuesta (Postman o similar).
- El resultado de la pestaña Actions de GitHub también sirve como evidencia de la corrida completa.
