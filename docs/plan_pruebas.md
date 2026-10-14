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
| CP-10 | Login correcto entrega token | Funcional | RF9 | usuario y contrasena validos | 200 con token y rol |  | PASA |  | `tests/test_auth.py` |
| CP-11 | Contrasena incorrecta | Seguridad - caso de error | RF9 | usuario valido con contrasena erronea | 401, mismo mensaje que para usuario inexistente |  | PASA |  | `tests/test_auth.py` |
| CP-12 | Login sin campos | Funcional - caso de error | RF9 | cuerpo vacio o sin contrasena | 400 |  | PASA |  | `tests/test_auth.py` |
| CP-13 | La contrasena se guarda con hash | Seguridad | RNF Seguridad | leer hash_contrasena de la base | no contiene la contrasena en texto plano |  | PASA |  | `tests/test_auth.py` |
| CP-14 | Registro valido | Funcional | RF1 | conductor registra un km mayor al actual en su camion | 201 y km_actual actualizado |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-15 | Km menor al actual | Funcional - caso de error | RF1 | km inferior al ultimo registrado | 400 y km_actual sin cambios |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-16 | Km igual al actual | Funcional - caso limite | RF1 | km identico al actual | definir y documentar la regla (aceptar o rechazar) |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-17 | Km negativo o no numerico | Funcional - caso de error | RF1 | -5, 'abc', 1500.5, null | 400 en todos los casos |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-18 | Camion inexistente | Funcional - caso de error | RF1 | id de camion que no existe | 404 |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-19 | Registro que cruza el umbral genera alerta | Funcional - flujo completo | RF1, RF3, RF4 | km que deja al camion dentro del umbral | estado alerta_temprana y alertas creadas |  | Pendiente |  | `tests/test_kilometraje.py` |
| CP-20 | Estado devuelve color del semaforo | Funcional | RF4 | conductor2 hace GET /camiones/2/estado (camion FLSG-22, en alerta temprana) | 200 con patente, km actual, estado y color amarillo | 200; estado alerta_temprana y color amarillo | Pasa | `evidencias/cp20_cp21_cp35_a_cp38_pasando.png` | `tests/test_estado.py` |
| CP-21 | Cada usuario ve solo sus alertas | Seguridad | RF9 | tres alertas para destinatarios distintos; conductor1, conductor2 y conductor3 hacen GET /alertas | cada usuario recibe solo las suyas; quien no tiene alertas recibe lista vacia | conductor1 y conductor2 reciben 1 alerta propia; conductor3 recibe lista vacia | Pasa | `evidencias/cp20_cp21_cp35_a_cp38_pasando.png` | `tests/test_estado.py` |
| CP-22 | Sin token se rechaza | Seguridad | RF9 | sin cabecera Authorization en POST /camiones/1/kilometraje | 401 | 401 | Pasa | `evidencias/cp22_a_cp26_pasando.png` | `tests/test_seguridad.py` |
| CP-23 | Conductor no registra en camion ajeno | Seguridad | RF9 | conductor1 (usuario 2) registra kilometraje en el camión 2 | 403 y ningún registro nuevo en registros_kilometraje | 403; el conteo de registros no cambia | Pasa | `evidencias/cp22_a_cp26_pasando.png` | `tests/test_seguridad.py` |
| CP-24 | Conductor no ve estado de camion ajeno | Seguridad | RF9 | conductor1 consulta GET /camiones/2/estado | 403 | 403 | Pasa | `evidencias/cp22_a_cp26_pasando.png` | `tests/test_seguridad.py` |
| CP-25 | Inyeccion sql en login | Seguridad | RNF Seguridad | POST /login con usuario ' OR '1'='1 | 401, sin error 500 | 401 | Pasa | `evidencias/cp22_a_cp26_pasando.png` | `tests/test_seguridad.py` |
| CP-26 | Token alterado o expirado | Seguridad | RF9 | token con un carácter del medio alterado; token emitido con TOKEN_DURACION_SEG = -1 | 401 en ambos | 401 en ambos | Pasa | `evidencias/cp22_a_cp26_pasando.png` | `tests/test_seguridad.py` |
| CP-35 | Los tres colores del semaforo | Funcional | RF4 | el jefe de flota consulta un camion en cada estado (camiones 1, 2 y 3) | 200 con color verde, amarillo y rojo segun el estado | 200 en los tres; colores verde, amarillo y rojo | Pasa | `evidencias/cp20_cp21_cp35_a_cp38_pasando.png` | `tests/test_estado.py` |
| CP-36 | Estado de camion inexistente | Funcional - caso de error | RF4 | id 999 y un id fuera del rango de la base (99999999999999999999) | 404, sin error 500 | 404 en ambos | Pasa | `evidencias/cp20_cp21_cp35_a_cp38_pasando.png` | `tests/test_estado.py` |
| CP-37 | Estado y alertas exigen token | Seguridad | RF9 | sin token; firma alterada; contenido cambiado a jefe_flota con la firma del conductor | 401 en los tres casos, en /camiones/1/estado y en /alertas | 401 en los tres casos y en ambas rutas | Pasa | `evidencias/cp20_cp21_cp35_a_cp38_pasando.png` | `tests/test_estado.py` |
| CP-38 | Conductor no ve estado de camion ajeno | Seguridad | RF9, RNF Seguridad | conductor1 consulta su camion, el de conductor2 y el camion sin conductor; el jefe consulta el camion sin conductor | 200 en el propio, 403 en los ajenos sin datos del camion, 200 para el jefe | 200, 403, 403 y 200 | Pasa | `evidencias/cp20_cp21_cp35_a_cp38_pasando.png` | `tests/test_estado.py` |

## Cómo dejar evidencia

- Ejecutar `pytest -v` y guardar la captura de la terminal en `docs/evidencias/` con el ID del caso en el nombre (ejemplo: `CP-15_falla.png`, `CP-15_pasa.png`).
- Para los endpoints, sumar una captura de la petición y la respuesta (Postman o similar).
- El resultado de la pestaña Actions de GitHub también sirve como evidencia de la corrida completa.
