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

### DEF-RF9-01 — Error HTTP 500 en POST /login

**Responsable:** Yerko Morales
**Módulo:** Autenticación RF9
**Prueba asociada:** CP-10
**Severidad:** Alta
**Estado:** Corregido y validado

#### 1. Descripción del defecto

Durante la integración del módulo de autenticación RF9, el equipo detectó que el endpoint `POST /login` respondía HTTP 500, impidiendo el inicio de sesión con credenciales válidas.

#### 2. Causa raíz


La implementación original consultaba la columna `usuario` y utilizaba `contrasena`, campos que no existen en la tabla `usuarios` del esquema SQLite oficial.

Los campos correctos son `nombre_usuario` y `hash_contrasena`.

Al reproducir la consulta defectuosa en una base SQLite temporal se obtuvo:

`sqlite3.OperationalError: no such column: usuario`

Esta reproducción confirma la incompatibilidad entre la consulta SQL y la estructura de la base de datos.


#### 3. Código antes de la corrección

Archivo: `app/auth.py`

La implementación original utilizaba una consulta SQL incompatible con el esquema oficial de SQLite.

```python
db = get_db()
cursor = db.execute(
    "SELECT * FROM usuarios WHERE usuario = ?",
    (usuario,)
)
user = cursor.fetchone()
```

**Error reproducido:**

```text
sqlite3.OperationalError: no such column: usuario
```

#### 4. Código después de la corrección

Archivo: `app/auth.py`

Se reemplazó la consulta SQL defectuosa por la función `buscar_usuario_por_nombre()` de `app/repositorio.py`, permitiendo consultar las columnas correspondientes al esquema oficial.

```python
registro = buscar_usuario_por_nombre(usuario.strip())

if registro is None or not verificar_contrasena(
    registro["hash_contrasena"], contrasena
):
    return jsonify(error="Credenciales inválidas"), 401

token = crear_token(registro["id"], registro["rol"])

return jsonify(token=token, rol=registro["rol"]), 200
```

#### 5. Verificación

- **Pruebas que lo confirman:** CP-10 a CP-13 (`tests/test_auth.py`) y CP-25 (`tests/test_seguridad.py`), todas pasan en la suite actual.
- **Evidencia de la nueva ejecución:** pendiente de captura por Yerko Morales (`docs/evidencias/cp10_pasando.png`). La captura de la falla puede obtenerse ejecutando CP-10 sobre el commit anterior a la corrección.
