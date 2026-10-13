# Revisión de seguridad OWASP Top 10 — prototipo FlotaSegura

Elaborada por Bryan Martinez (Integrante F, 13-10-2026). Revisada y corregida por Felipe Aravena el mismo día: se reasignaron las categorías a las pruebas que realmente las cubren y se dejó solo lo que tiene evidencia en el código o en las pruebas (ver `docs/registro_incidencias.md`).

Versión de referencia: OWASP Top 10 (2021). Se revisaron 6 categorías sobre el módulo de registro de kilometraje, cálculo de mantención y alertas. Cada fila indica si la categoría aplica al prototipo, qué se encontró y dónde está la evidencia. Los hallazgos abiertos se dejan como tales: la revisión es sobre el prototipo real, no sobre el sistema completo diseñado en la Evaluación 2.

## Resumen

| Categoría | ¿Aplica? | Resultado | Evidencia |
|---|---|---|---|
| A01:2021 Pérdida de control de acceso | Sí | Cubierta, sin hallazgos | `app/permisos.py`; CP-21, CP-23, CP-24, CP-29, CP-32, CP-38 |
| A02:2021 Fallas criptográficas | Sí | Cubierta en parte, 2 hallazgos | `app/auth.py`, `app/seed.py`, `app/config.py`; CP-13, CP-26 |
| A03:2021 Inyección | Sí | Cubierta, sin hallazgos | `app/repositorio.py`, `app/alertas.py`; CP-17, CP-25 |
| A05:2021 Configuración de seguridad incorrecta | Sí | 2 hallazgos | `app/config.py`, `app/seed.py`, `run.py` |
| A07:2021 Fallas de identificación y autenticación | Sí | Cubierta en parte, 2 hallazgos | `app/auth.py`, `app/permisos.py`; CP-10 a CP-13, CP-22, CP-26, DEF-RF9-01 |
| A09:2021 Fallas en el registro y monitoreo | Sí | 1 hallazgo | `app/auth.py`, `app/rutas_kilometraje.py` |

Categorías no revisadas: A04 (diseño inseguro), A06 (componentes vulnerables y desactualizados), A08 (fallas de integridad de software y datos) y A10 (SSRF). A06 y A10 no aplican a un prototipo local sin dependencias auditadas ni llamadas a servicios externos; A04 y A08 exceden el alcance de esta revisión.

## Detalle por categoría

### A01:2021 — Pérdida de control de acceso

**Aplica:** sí. Hay dos roles (conductor y jefe de flota) y la regla de negocio de que un conductor solo opera sobre su camión asignado.

**Qué se encontró:** todos los endpoints de datos exigen token (`@login_requerido`) y la regla de camión asignado está centralizada en `puede_acceder_a_camion()` (`app/permisos.py`), que usan tanto el registro de kilometraje como la consulta de estado. Las alertas se filtran por el usuario del token, no por un parámetro de la petición (`app/rutas_estado.py`). Un token válido cuyo usuario ya no existe en la base se rechaza con 401.

**Evidencia:** CP-23 (conductor registra en camión ajeno → 403, sin registro guardado), CP-24 y CP-38 (conductor consulta camión ajeno → 403, sin datos del camión en la respuesta), CP-21 (cada usuario ve solo sus alertas), CP-29 (el jefe de flota accede a cualquier camión), CP-32 (token de usuario inexistente → 401).

**Hallazgos:** ninguno en el alcance del prototipo. El decorador `rol_requerido` existe pero ningún endpoint lo usa todavía, porque la regla vigente se resuelve con `puede_acceder_a_camion`.

### A02:2021 — Fallas criptográficas

**Aplica:** sí. El sistema guarda contraseñas y emite tokens firmados.

**Qué se encontró:** las contraseñas se guardan con hash y sal generados por `werkzeug.security.generate_password_hash` (algoritmo scrypt), nunca en texto plano (`app/seed.py`, `app/auth.py`). Los tokens se firman con `itsdangerous.URLSafeTimedSerializer` y se verifican firma y antigüedad al leerlos. Una firma alterada o un contenido modificado se rechazan.

**Evidencia:** CP-13 (el hash guardado no contiene la contraseña y se verifica correctamente), CP-26 y CP-37 (token alterado o vencido → 401; contenido de jefe de flota con firma de conductor → 401).

**Hallazgos abiertos:**
1. El prototipo se ejecuta con el servidor de desarrollo de Flask sobre HTTP. Credenciales y tokens viajan sin cifrar. El RNF de seguridad de la Evaluación 2 exige HTTPS; corresponde al despliegue, no al código.
2. El contenido del token no está cifrado, solo firmado: cualquiera que lo vea puede leer el id y el rol del usuario. No expone contraseñas ni datos adicionales.

### A03:2021 — Inyección

**Aplica:** sí. Todas las operaciones leen o escriben en SQLite con datos que vienen del usuario.

**Qué se encontró:** todas las consultas de `app/repositorio.py` y las inserciones de `app/alertas.py` usan parámetros (`?`); no hay SQL construido concatenando texto. El kilometraje se valida como entero antes de usarse (`validar_kilometraje`), lo que descarta cadenas como `1; DROP TABLE camiones;--`.

**Evidencia:** CP-25 (usuario `' OR '1'='1` en el login → 401, sin error 500), CP-17 (valores no numéricos, incluida una cadena con `DROP TABLE`, → 400 sin tocar la base).

**Hallazgos:** ninguno.

### A05:2021 — Configuración de seguridad incorrecta

**Aplica:** sí.

**Qué se encontró:** el servidor no se ejecuta en modo debug (`run.py`, `debug=False`), por lo que un error interno responde una página genérica y no expone trazas al cliente.

**Hallazgos abiertos:**
1. `app/config.py` trae una clave de firma por defecto (`clave-solo-para-desarrollo`) que se usa si no existe la variable de entorno `FLOTASEGURA_SECRET_KEY`. En un despliegue real, cualquiera que conozca el código podría firmar tokens. La clave debe venir siempre del entorno o de un gestor de secretos, sin valor por defecto.
2. `app/seed.py` contiene una contraseña de prueba común a los cuatro usuarios. Es aceptable para la base local de desarrollo y está declarada como tal, pero el seed no debe ejecutarse en producción.

### A07:2021 — Fallas de identificación y autenticación

**Aplica:** sí.

**Qué se encontró:** el login responde el mismo mensaje y el mismo código (401) para usuario inexistente y para contraseña incorrecta, lo que evita enumerar usuarios. Los campos de entrada se validan antes de consultar. El token caduca a los 3600 segundos (`TOKEN_DURACION_SEG`). Durante la integración se detectó y corrigió un defecto en este punto: el login respondía 500 con cualquier credencial (DEF-RF9-01 en la bitácora).

**Evidencia:** CP-10 a CP-13 (`tests/test_auth.py`), CP-22 (sin token → 401), CP-26 (token vencido → 401).

**Hallazgos abiertos:**
1. No hay límite de intentos de inicio de sesión ni bloqueo temporal, así que el login es susceptible a fuerza bruta. Recomendación de Bryan Martinez: bloquear la cuenta o aplicar espera tras 5 intentos fallidos.
2. No hay cierre de sesión: un token emitido es válido hasta que caduca y no puede invalidarse antes. Recomendación: mantener una lista de tokens revocados o acortar la duración.

### A09:2021 — Fallas en el registro y monitoreo

**Aplica:** sí. El sistema existe para detectar a tiempo mantenciones vencidas; también debería poder detectar accesos indebidos.

**Qué se encontró:** el único registro que escribe la aplicación es el error de un notificador en `app/rutas_kilometraje.py`. Los intentos de login fallidos, los tokens rechazados y los accesos denegados (401 y 403) no quedan registrados en ninguna parte.

**Hallazgo abierto:** sin registro de eventos de seguridad no es posible detectar un ataque de fuerza bruta ni un intento de acceder a camiones ajenos. Recomendación: registrar con `current_app.logger` cada 401 y 403, con usuario, ruta y hora.

## Relación con la bitácora y con ISO 27001

Los hallazgos de A05 y A07 se dejan abiertos porque no son defectos funcionales del prototipo sino mejoras de seguridad fuera del alcance comprometido. Los defectos de seguridad que sí se corrigieron (DEF-RF9-01, DEF-D1 a DEF-D3) están en `docs/bitacora_defectos.md` con sus controles ISO/IEC 27001 asociados.
