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
* **Desalineación con el Esquema**: La implementación inicial de los métodos `actualizar` en los notificadores (`NotificadorJefeFlota` y `NotificadorConductor`) realizaba consultas `INSERT` incompletas que omitían campos obligatorios exigidos por el contrato de la base de datos (`plan_id`, `destinatario_id`, `nivel`).
* **Restricciones de Integridad Referencial**: Las pruebas enviaban IDs simulados que no existían previamente en las tablas relacionales del entorno de prueba (`usuarios`, `camiones`, `planes_mantencion`), lo que activaba los bloqueos por *Foreign Key*.

#### 3. Solución Aplicada
1. **Actualización de Consultas SQL**: Se reestructuraron las consultas parametrizadas en `app/alertas.py` para insertar de manera correcta todos los atributos requeridos por el esquema (`camion_id`, `plan_id`, `destinatario_id`, `nivel`, `mensaje`).
2. **Preparación de Datos en Pruebas (`Fixtures`)**: Se modificaron las funciones de prueba en `tests/test_alertas.py` para insertar previamente los registros dependientes necesarios (usuarios con roles válidos, camiones y planes de mantención) mediante consultas del tipo `INSERT OR REPLACE` antes de ejecutar la notificación del sujeto.

#### 4. Verificación y Estado
- **Estado**: Resuelto y Verificado.
- **Evidencia**: Tras la corrección y el reenvío de los cambios al repositorio remoto, todas las pruebas unitarias asociadas al Patrón Observer (`CP-06`, `CP-07`, `CP-08`, `CP-09`) completaron su ejecución con éxito, obteniendo el estado de compilación aprobada en GitHub Actions.

