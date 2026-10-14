# Reparto de trabajo — 6 integrantes

Esta tabla es la base de la **tabla de aporte individual** del informe (criterio 9) y debe coincidir con el historial de commits. Reparto vigente desde el 12-10-2026 (ver `docs/registro_incidencias.md`).

| Integrante | Código | Pruebas | Sección del informe |
|---|---|---|---|
| **A** — Benjamin Jofre | `app/estrategias.py` (Strategy) | `tests/test_estrategias.py` (CP-01 a CP-05) | Criterio 1: justificación del módulo, trazabilidad y patrones |
| **B** — Michael Rabelo | `app/alertas.py` (Observer) y `app/permisos.py` (RBAC) | `tests/test_alertas.py` (CP-06 a CP-09) | Criterio 3: UML actualizados y registro de cambios |
| **C** — Yerko Morales | `app/auth.py` (login, hash, token) | `tests/test_auth.py` (CP-10 a CP-13) | Criterio 5: confiabilidad, ética y Ley 21.459 |
| **D** — Widjy Marcellus | `app/rutas_kilometraje.py` (registro y validaciones) | `tests/test_kilometraje.py` (CP-14 a CP-19 y CP-27 a CP-34) | Criterio 7: plan y ejecución de pruebas |
| **E** — Felipe Aravena | `app/repositorio.py`, `app/seed.py`, `app/rutas_estado.py`, estructura inicial del proyecto y `.github/workflows/pruebas.yml` | `tests/test_estado.py` (CP-20, CP-21 y CP-35 a CP-38) | Criterios 2 y 4: retrospectiva de proceso y tendencias cloud. Coordinación e integración |
| **F** — Bryan Martinez | — | `tests/test_seguridad.py` (CP-22 a CP-26) | Criterios 6 y 8: revisión OWASP (`docs/revision_owasp.md`) y bitácora de defectos con controles ISO 27000 |

Las pruebas de seguridad y los dos documentos de Bryan Martinez recibieron una corrección de integración de Felipe Aravena el 13-10-2026, registrada en `docs/registro_incidencias.md`.

## Reglas para los commits

- Cada integrante hace commits **desde su propia cuenta** de GitHub. El docente revisa el historial por persona.
- Commits pequeños y frecuentes, con mensaje que diga qué se hizo. Ejemplo: `Implementa CalculoPorKm (RF3)`.
- Trabajar siempre sobre un clon, hacer Pull antes de empezar y antes de cada Push. Nunca subir un archivo con marcas `<<<<<<<` / `>>>>>>>`.
- Nada de force push ni de modificar commits ya publicados.

## Reglas para los defectos (criterio 8)

Cuando una prueba falle, **no corregir en silencio**. El orden es:

1. Guardar la captura de la prueba fallando en `docs/evidencias/`.
2. Hacer commit del código tal como está, con la prueba que falla.
3. Anotar el defecto en `docs/bitacora_defectos.md` (descripción, causa, severidad).
4. Corregir y hacer commit aparte.
5. Ejecutar la prueba de nuevo y guardar la captura pasando.
