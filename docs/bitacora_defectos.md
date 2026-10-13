# Bitácora de defectos

Registro de los defectos reales encontrados al ejecutar las pruebas del prototipo, con su causa, el código antes y después de la corrección y la evidencia de la nueva ejecución.

Mantenida por el Integrante F (Bryan Martinez). Restaurada y consolidada por Felipe Aravena el 13-10-2026, después de que una subida sobrescribiera el archivo (ver `docs/registro_incidencias.md`). Cada defecto lo documenta quien lo corrigió.

Severidad: `Crítica` (compromete seguridad o datos), `Alta` (el módulo entrega un resultado incorrecto o no funciona), `Media`, `Baja`.

## Resumen

| ID | Prueba que lo detectó | Descripción | Causa | Severidad | Estado | Documentado por |
|---|---|---|---|---|---|---|
| DEF-01 | CP-06, CP-07 | Las inserciones en la tabla `alertas` omitían columnas obligatorias y violaban llaves foráneas | Consulta `INSERT` incompleta respecto del esquema; datos de prueba sin las filas relacionadas | Alta | Corregido y verificado (CP-06 a CP-09 pasan) | Michael Rabelo |
| DEF-RF9-01 | CP-10 | `POST /login` respondía HTTP 500 con cualquier credencial | La consulta usaba las columnas `usuario` y `contrasena`, que no existen (`nombre_usuario`, `hash_contrasena`) | Alta | Corregido y verificado (CP-10 a CP-13 y CP-25 pasan) | Yerko Morales |
| DEF-D1 a DEF-D4 | CP-31 a CP-34 | Defectos de validación de entradas y tolerancia a fallos en el registro de kilometraje (id fuera de rango, token de usuario inexistente, cuerpo demasiado grande, falla de un notificador) | Ver `INFORME_INTEGRANTE_D.md` | Media a Alta | Corregidos y verificados (CP-31 a CP-34 pasan). Pendiente trasladar el detalle con código antes y después a esta bitácora | Widjy Marcellus |

## Controles ISO/IEC 27001 vinculados a las correcciones de seguridad

Numeración del Anexo A de ISO/IEC 27001:2013. Selección inicial de Bryan Martinez; completada por Felipe Aravena.

| Control | Defecto | Riesgo al que responde |
|---|---|---|
| **A.9.4.2 — Procedimientos seguros de inicio de sesión** | DEF-RF9-01 | Mientras el login respondía 500, ningún usuario podía autenticarse y el error exponía detalles internos en el registro del servidor. La corrección deja un único mensaje para usuario inexistente y contraseña incorrecta, valida los campos de entrada y no revela cuál de los dos falló. |
| **A.9.4.1 — Restricción del acceso a la información** | DEF-D2 (token firmado de un usuario que ya no existe) | Un token válido podía seguir usándose después de eliminar al usuario. La corrección en `app/permisos.py` verifica que el usuario del token exista en la base antes de autorizar, y responde 401 si no. |
| **A.14.2.5 — Principios de ingeniería de sistemas seguros** | DEF-D1 y DEF-D3 (id fuera de rango, cuerpo mayor a 1 MB) | Entradas no validadas provocaban errores 500 o permitían agotar recursos del servidor. Las correcciones en `app/rutas_kilometraje.py` y `app/repositorio.py` validan rango y tamaño antes de procesar, y responden 404 y 413. |

## Detalle por defecto

### Defectos del módulo de alertas (Integrante B)

* **Responsable / Integrante:** Michael Rabelo (Integrante B)
* **Módulo:** `app/alertas.py` (Patrón Observer)

### DEF-01: Incompatibilidad en columnas de inserción y restricciones de Llaves Foráneas (FK) en la tabla `alertas`

- **Fecha de Detección**: Octubre de 2026
- **Pruebas Asociadas**: `test_cp_06_al_cruzar_umbral_se_alerta_a_jefe_y_conductor`, `test_cp_07_camion_sin_conductor_solo_alerta_al_jefe`
- **Severidad**: Alta (Bloqueaba el pipeline de integración continua en GitHub Actions)

#### 1. Descripción del Problema (Fallo)
Al ejecutar inicialmente el conjunto de pruebas para el servicio de alertas (`app/alertas.py`), el servidor de pruebas (`pytest`) arrojó múltiples errores de integridad en SQLite:
1. `sqlite3.OperationalError: table alertas has no column named tipo`
2. `sqlite3.IntegrityError: NOT NULL constraint failed: alertas.plan_id` / `destinatario_id` / `nivel`
3. `sqlite3.IntegrityError: FOREIGN KEY constraint failed`

#### 2. Causa Raíz
- **Desalineación con el Esquema**: La implementación inicial de los métodos `actualizar` en los notificadores (`NotificadorJefeFlota` y `NotificadorConductor`) realizaba consultas `INSERT` incompletas que omitían campos obligatorios exigidos por el contrato de la base de datos (`plan_id`, `destinatario_id`, `nivel`).
- **Restricciones de Integridad Referencial**: Las pruebas enviaban IDs simulados que no existían previamente en las tablas relacionales del entorno de prueba (`usuarios`, `camiones`, `planes_mantencion`), lo que activaba los bloqueos por *Foreign Key*.

#### 3. Solución Aplicada y Código de Cambio
- **Código ANTES:**
  ```python
  # Inserción fija y parcial que omitía llaves y campos requeridos
  cursor.execute(
      "INSERT INTO alertas (camion_id, mensaje) VALUES (?, ?)",
      (camion['id'], mensaje)
  )
  ```
- **Código DESPUES:**
  ```python
  # Inserción completa parametrizada respetando el esquema relacional
  cursor.execute(
      "INSERT INTO alertas (camion_id, plan_id, destinatario_id, nivel, mensaje) VALUES (?,?,?,?,?)",
      (camion['id'], plan_mantencion.plan_id, jefe_id, plan_mantencion.estado, mensaje)
  )
  ```

#### 4. Verificación y Estado
- **Estado**: Resuelto y Verificado.
- **Evidencia**: Tras la corrección y el reenvío de los cambios al repositorio remoto, todas las pruebas unitarias asociadas al Patrón Observer (`CP-06`, `CP-07`, `CP-08`, `CP-09`) completaron su ejecución con éxito, obteniendo el estado de compilación aprobada en GitHub Actions.

#### 5. Evidencias

* **Prueba Fallando:**
  ![Prueba fallando](evidencias/cp06_fallando.png)
* **Prueba Pasando (Verde):**
  ![Prueba pasando](evidencias/cp06_pasando.png)

---


## DEF-D1: Error 500 por Desbordamiento de Enteros en `camion_id` (SQLite Overflow)
* **Requerimiento:** RF1 (Registro de Kilometraje)
* **Caso de Prueba:** CP-31
* **Severidad:** Media / Alta
* **Descripción:** Al enviar un `camion_id` numérico fuera del rango estándar de enteros de SQLite (ej. `99999999999999999999`), el motor lanzaba una excepción `OverflowError` no capturada, respondiendo con un error HTTP `500 Internal Server Error`.

#### Código Antes (Defectuoso)
```python
@app.route('/camiones/<int:camion_id>/kilometraje', methods=['POST'])
def registrar_kilometraje(camion_id):
    # Consulta directa sin validar rangos
    camion = repositorio.obtener_camion_por_id(camion_id)
    if not camion:
        return jsonify({"error": "Camión no encontrado"}), 404

### Código Corrigido
 @app.route('/camiones/<int:camion_id>/kilometraje', methods=['POST'])
def registrar_kilometraje(camion_id):
    # Validar límite de enteros de SQLite antes de consultar la BD
    if camion_id > 9223372036854775807 or camion_id < 1:
        return jsonify({"error": "ID de camión fuera de rango válido"}), 404
    
    try:
        camion = repositorio.obtener_camion_por_id(camion_id)
    except (OverflowError, ValueError):
        return jsonify({"error": "ID de camión inválido"}), 404

    if not camion:
        return jsonify({"error": "Camión no encontrado"}), 404

## DEF-D2: Falta de Verificación de Integridad de Usuario en Decorador JWT ##
Requerimiento: RF1, RF9 (Autenticación y Autorización RBAC)

Caso de Prueba: CP-32

Severidad: Alta (Seguridad)

Descripción: El decorador @login_requerido solo validaba la firma del token JWT (jwt.decode). Si un usuario activo obtenía un token y posteriormente era eliminado de la base de datos, el token continuaba permitiéndole operar.

def login_requerido(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = obtener_token_header()
        datos = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        g.usuario_id = datos["usuario_id"]
        g.rol = datos["rol"]
        return f(*args, **kwargs)
    return decorated

## Código Después (Corregido)
def login_requerido(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = obtener_token_header()
        datos = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # Consulta explícita a la BD para verificar existencia real del usuario
        usuario = repositorio.obtener_usuario_por_id(datos["usuario_id"])
        if not usuario or not usuario.get("activo", True):
            return jsonify({"error": "Usuario inactivo o no encontrado"}), 401
            
        g.usuario_id = datos["usuario_id"]
        g.rol = datos["rol"]
        return f(*args, **kwargs)
    return decorated

<<<<<<< HEAD
DEF-D3: Ausencia de Límite en Tamaño de Payload HTTP (Vulnerabilidad DoS)
Requerimiento: RF1 (Robustez API)

Caso de Prueba: CP-33

Severidad: Media

Descripción: La ruta permitía solicitudes HTTP POST con payloads arbitrariamente grandes, permitiendo consumo excesivo de recursos antes de procesar la solicitud.

## Código Antes (Defectuoso)
@app.route('/camiones/<int:camion_id>/kilometraje', methods=['POST'])
def registrar_kilometraje(camion_id):
    datos = request.get_json()
    # Procesamiento sin validar el tamaño máximo del cuerpo HTTP

# Configuración global en app.py / rutas_kilometraje.py
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # Límite de 1 MB

## Código Después (Corregido)
@app.errorhandler(413)
def payload_demasiado_grande(error):
    return jsonify({"error": "El payload excede el tamaño máximo permitido (1 MB)"}), 413

DEF-D4: Excepciones No Capturadas en Observadores de Notificación
Requerimiento: RF1, RF4 (Tolerancia a Fallos / Patrón Observer)

Caso de Prueba: CP-34

Severidad: Alta (Resiliencia)

Descripción: Al cambiar el estado de un camión, si uno de los suscriptores (NotificadorJefeFlota o NotificadorConductor) lanzaba una excepción por fallo de red o servicio externo, interrumpía el flujo del endpoint arrojando 500 y dejando en duda el guardado del kilometraje.

Código Antes (Defectuoso)
if nuevo_estado in ['alerta_temprana', 'mantencion_vencida']:
    # Si notificar() falla, la ruta completa arroja 500 Internal Server Error
    sujeto_camion.notificar(camion_id, nuevo_estado, nuevo_km)

## Código Después (Corregido)
if nuevo_estado in ['alerta_temprana', 'mantencion_vencida']:
    try:
        sujeto_camion.notificar(camion_id, nuevo_estado, nuevo_km)
    except Exception as e:
        # Aislamiento del fallo del servicio de notificaciones
        logger.error(f"Error no crítico en observador de notificaciones: {e}")

return jsonify({"mensaje": "Kilometraje registrado exitosamente", "estado": nuevo_estado}), 201
Resultado Obtenido: La transacción del kilometraje se guarda correctamente y retorna 201 Created tolerando fallos de red.
=======
return jsonify(token=token, rol=registro["rol"]), 200
```

#### 5. Verificación

- **Pruebas que lo confirman:** CP-10 a CP-13 (`tests/test_auth.py`) y CP-25 (`tests/test_seguridad.py`), todas pasan en la suite actual.
- **Evidencia de la nueva ejecución:** pendiente de captura por Yerko Morales (`docs/evidencias/cp10_pasando.png`). La captura de la falla puede obtenerse ejecutando CP-10 sobre el commit anterior a la corrección.
>>>>>>> 5bd2fa9425054a209b22d60a5e21de0a4be60531
