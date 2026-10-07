# Reparto de trabajo — 6 integrantes

Reemplazar las letras por los nombres. Esta tabla es la base de la **tabla de aporte individual** del informe (criterio 9) y debe coincidir con el historial de commits.

| Integrante | Código | Pruebas | Sección del informe |
|---|---|---|---|
| **A** — Benjamin Jofre | `app/estrategias.py` (Strategy) | `tests/test_estrategias.py` (CP-01 a CP-05) | Criterio 1: justificación del módulo, trazabilidad y patrones |
| **B** — _nombre_ | `app/alertas.py` (Observer) | `tests/test_alertas.py` (CP-06 a CP-09) | Criterio 3: UML actualizados y registro de cambios |
| **C** — _nombre_ | `app/auth.py` (login, hash, token) | `tests/test_auth.py` (CP-10 a CP-13) | Criterio 5: confiabilidad, ética y Ley 21.459 |
| **D** — _nombre_ | `app/rutas_kilometraje.py` (registro y validaciones) | `tests/test_kilometraje.py` (CP-14 a CP-19) | Criterio 7: plan y ejecución de pruebas |
| **E** — _nombre_ | `app/repositorio.py`, `app/seed.py`, `app/rutas_estado.py` | `tests/test_estado.py` (CP-20 y CP-21) | Criterios 2 y 4: retrospectiva de proceso y tendencias cloud |
| **F** — _nombre_ | `app/permisos.py` (RBAC), `.github/workflows/pruebas.yml` | `tests/test_seguridad.py` (CP-22 a CP-26) | Criterios 6 y 8: OWASP, bitácora de defectos e ISO 27000 |

El criterio 9 (integración y revisión final del informe) lo cierra todo el grupo el martes 13.

## Orden de trabajo

Algunos frentes dependen de otros. Para no bloquearse:

1. **Primero (miércoles 7):** E entrega `repositorio.py` y `seed.py`; C entrega `auth.py`; A entrega `estrategias.py`. No dependen de nadie.
2. **Después (jueves 8):** B entrega `alertas.py` (usa el resultado de A); F entrega `permisos.py` (usa `leer_token` de C).
3. **Al final (jueves 8 y viernes 9):** D arma `rutas_kilometraje.py` y E arma `rutas_estado.py`, que conectan todo lo anterior.

Los nombres de funciones y sus parámetros ya están definidos en cada archivo. Si alguien necesita cambiarlos, avisa al grupo antes.

## Reglas para los commits

- Cada integrante hace commits **desde su propia cuenta** de GitHub. El docente revisa el historial por persona.
- Commits pequeños y frecuentes, con mensaje que diga qué se hizo. Ejemplo: `Implementa CalculoPorKm (RF3)`.
- Un commit gigante el último día se ve como aporte no verificable.

## Reglas para los defectos (criterio 8, 12 puntos)

Cuando una prueba falle, **no corregir en silencio**. El orden es:

1. Guardar la captura de la prueba fallando en `docs/evidencias/`.
2. Hacer commit del código tal como está, con la prueba que falla. Ejemplo: `Agrega CP-15, falla: acepta km menor al actual`.
3. Anotar el defecto en `docs/bitacora_defectos.md` (descripción, causa, severidad).
4. Corregir y hacer commit aparte. Ejemplo: `Corrige DEF-01: valida km contra km_actual`.
5. Ejecutar la prueba de nuevo y guardar la captura pasando.

Así quedan el antes, el después y la nueva ejecución que pide la rúbrica.
