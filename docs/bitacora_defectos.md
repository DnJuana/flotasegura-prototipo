# Bitácora de defectos

Responsable de mantenerla: Integrante F. Cada integrante anota los defectos que encuentre en sus pruebas.

La rúbrica pide al menos 3 defectos **reales**, encontrados al ejecutar las pruebas. Aquí solo se registra lo que efectivamente falló. Ver el procedimiento en `REPARTO.md`.

Severidad: `Crítica` (compromete seguridad o datos), `Alta` (el módulo entrega un resultado incorrecto), `Media`, `Baja`.

## Resumen

| ID | Prueba que lo detectó | Descripción | Causa | Severidad | Commit con la falla | Commit de la corrección | Nueva ejecución |
|---|---|---|---|---|---|---|---|
| DEF-01 |  |  |  |  |  |  |  |

## Detalle por defecto

Copiar este bloque por cada defecto.

### DEF-01 — título

- **Prueba que lo detectó:** CP-XX
- **Descripción:** qué se esperaba y qué ocurrió.
- **Causa:** por qué ocurrió.
- **Severidad:**
- **Evidencia de la falla:** `docs/evidencias/CP-XX_falla.png`

**Código antes**

```python
```

**Código después**

```python
```

- **Evidencia de la nueva ejecución:** `docs/evidencias/CP-XX_pasa.png`
- **Control ISO 27000 relacionado** (solo si es un defecto de seguridad): control, y riesgo al que responde.
# Bitácora de Defectos - Proyecto FlotaSegura

Este documento registra los defectos encontrados durante el ciclo de pruebas unitarias e integración, siguiendo las directrices de trazabilidad del proyecto.

---
# Bitácora de Defectos — Módulo de Alertas (Patrón Observer)

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
- **Código DESPUES:**
  # Inserción completa parametrizada respetando el esquema relacional
  cursor.execute(
      "INSERT INTO alertas (camion_id, plan_id, destinatario_id, nivel, mensaje) VALUES (?,?,?,?,?)",
      (camion['id'], plan_mantencion.plan_id, jefe_id, plan_mantencion.estado, mensaje)
  )
  
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
