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

- **Responsable / Integrante:** Michael Rabelo
- **Módulo:** `app/alertas.py` (Patrón Observer)

---

### Tabla Resumen de Defectos

| ID | Módulo / Componente | Descripción Resumida | Severidad | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-01** | `app/alertas.py` | Incompatibilidad de columnas y llaves foráneas en inserción de `alertas` | Alta | Resuelto |
| **DEF-02** | `app/alertas.py` | Asignación de destinatario con ID fijo (`1`) en `NotificadorJefeFlota` | Media | Resuelto |

---

DEF-01: Incompatibilidad en columnas de inserción y restricciones de Llaves Foráneas (FK) en la tabla `alertas`

- **Fecha de Detección**: Octubre de 2026
- **Pruebas Asociadas**: `test_cp_06_al_cruzar_umbral_se_alerta_a_jefe_y_conductor`, `test_cp_07_camion_sin_conductor_solo_alerta_al_jefe`
- **Severidad**: Alta (Bloqueaba la ejecución del pipeline)

 1. Descripción del Problema (Fallo)
Al ejecutar el conjunto de pruebas para el servicio de alertas (`app/alertas.py`), el servidor de pruebas (`pytest`) arrojaba errores de SQLite por columnas faltantes (`plan_id`, `nivel`, `destinatario_id`) debido a inserciones incompletas.

 2. Causa Raíz
- **Desalineación con el Esquema**: La implementación inicial realizaba consultas `INSERT` incompletas que omitían campos obligatorios exigidos por el contrato de la base de datos.

 3. Código ANTES:
```python
# Inserción parcial e incompleta que omitía campos requeridos por la tabla
cursor.execute(
    "INSERT INTO alertas (camion_id, mensaje) VALUES (?, ?)",
    (camion['id'], mensaje)
)

 4. Código DESPUÉS:
# Inserción parametrizada que incluye todas las columnas obligatorias del esquema relacional
cursor.execute(
    "INSERT INTO alertas (camion_id, plan_id, destinatario_id, nivel, mensaje) VALUES (?,?,?,?,?)",
    (camion['id'], plan_mantencion.plan_id, 1, plan_mantencion.estado, mensaje)
)

 5. Verificación y Estado
- Estado: Resuelto y Verificado.
Evidencia: Las pruebas del patrón observer registraron filas correctamente en la base de datos de pruebas sin violar las restricciones del esquema.

DEF-02: Destinatario fijo del Jefe de Flota en lugar de búsqueda dinámica
Fecha de Detección: Octubre de 2026
Pruebas Asociadas: test_cp_06_al_cruzar_umbral_se_alerta_a_jefe_y_conductor
Severidad: Media (Mejora de arquitectura y escalabilidad del rol)

 1. Descripción del Problema (Fallo)
El NotificadorJefeFlota utilizaba un ID de destinatario quemado o fijo (destinatario_id = 1), lo cual impedía notificar a otros administradores o adaptarse si el ID variaba en la base de datos.

 2. Causa Raíz
Asignación Estática: Se asumía que el ID del jefe de flota siempre sería 1, omitiendo la consulta dinámica a la tabla usuarios para el rol jefe_flota.

 3. Código ANTES:
# Asignación de destinatario estática con ID fijo
cursor.execute(
    "INSERT INTO alertas (camion_id, plan_id, destinatario_id, nivel, mensaje) VALUES (?,?,?,?,?)",
    (camion['id'], plan_mantencion.plan_id, 1, plan_mantencion.estado, mensaje)
)

 4. Código DESPUÉS:
# Búsqueda dinámica y automatizada de todos los usuarios con rol 'jefe_flota'
cursor.execute("SELECT id FROM usuarios WHERE rol = 'jefe_flota'")
jefes = cursor.fetchall()

for jefe in jefes:
    jefe_id = jefe[0]
    cursor.execute(
        "INSERT INTO alertas (camion_id, plan_id, destinatario_id, nivel, mensaje) VALUES (?,?,?,?,?)",
        (camion['id'], plan_mantencion.plan_id, jefe_id, plan_mantencion.estado, mensaje)
    )

 5. Evidencias
 Estado: Resuelto y Verificado.
Evidencia: Las pruebas que validan las alertas al jefe de flota pasan exitosamente y notifican a todos los usuarios que poseen el rol jefe_flota registrados en la base de datos.
* **Prueba Fallando:**
  ![Prueba fallando](evidencias/cp06_fallando.png)
* **Prueba Pasando (Verde):**
  ![Prueba pasando](evidencias/cp06_pasando.png)