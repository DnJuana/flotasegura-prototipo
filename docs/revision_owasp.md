# Revisión de Seguridad OWASP - Proyecto FlotaSegura

## Resumen de Pruebas de Seguridad (CP-22 a CP-26)

| Caso de Prueba | Vulnerabilidad OWASP Evaluada | Estado | Observaciones / Riesgo |
|---|---|---|---|
| **CP-22** | A03:2021 - Inyección (SQL/NoSQL) | **PASÓ** | Endpoints sanitizan entrada; se bloquean payloads maliciosos. |
| **CP-23** | A01:2021 - Control de Acceso Roto | **PASÓ** | Rutas protegidas responden `401 Unauthorized` sin token JWT válido. |
| **CP-24** | A02:2021 - Fallos Criptográficos | **PASÓ** | Tráfico y tokens viajan encriptados; contraseñas con hash seguro. |
| **CP-25** | A07:2021 - Identificación y Autenticación | **FALLÓ** | Defecto reportado en módulo de Login (pendiente de corrección por Yerko). |
| **CP-26** | A05:2021 - Configuración Incorrecta de Seguridad | **PASÓ** | Encabezados HTTP configurados y manejo de errores sin leak de stack traces. |

---

## Recomendaciones para Mitigación (CP-25)
1. Implementar bloqueo de cuenta tras 5 intentos fallidos de inicio de sesión.
2. Forzar vencimiento e invalidación de JWT al cerrar sesión.