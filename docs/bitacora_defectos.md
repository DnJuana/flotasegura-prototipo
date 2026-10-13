# Bitácora de Defectos y Mapeo ISO/IEC 27001 - FlotaSegura

| ID Defecto | Caso de Prueba | Descripción del Defecto | Severidad | Estado | Control ISO 27001 Asociado |
|---|---|---|---|---|---|
| **DEF-001** | CP-25 | Fallo en validación/respuesta del Login bajo credenciales inválidas o fuerza bruta. | Alta | Abierto | **A.9.4.2** (Procedimientos seguros de inicio de sesión) |

---

## Notas de Integración
* **Responsable de la corrección:** Yerko (Integrante de Desarrollo).
* **Verificación pendiente:** Re-ejecución de `pytest tests/test_seguridad.py::test_cp25_autenticacion_segura` una vez aplicado el fix por el equipo de desarrollo.