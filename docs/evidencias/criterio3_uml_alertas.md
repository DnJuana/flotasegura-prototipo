# Criterio 3: UML Actualizados y Registro de Cambios - Módulo de Alertas (Observer)

## 1. Diagrama de Clases (Patrón Observer - RF4)
A continuación se presenta el diagrama de clases actualizado que modela el servicio de notificaciones y persistencia de alertas:

![Diagrama Observer](evidencias/diagrama_observer.png)

## 2. Descripción y Justificación del Componente
* **Estructura del Patrón:** La clase `SujetoCamion` administra la lista de observadores activos. Cuando se detecta un cambio crítico de estado, se invoca de forma polimórfica el método `actualizar()` sobre la interfaz abstracta `ObservadorMantencion`.
* **Implementación Concreta:** Las clases `NotificadorJefeFlota` y `NotificadorConductor` implementan la interfaz para persistir las alertas directamente en la base de datos SQLite mediante consultas parametrizadas, cumpliendo con las restricciones de integridad y llaves foráneas (`FOREIGN KEY`, `NOT NULL`).
* **Evolución Tecnológica:** Respecto al diseño conceptual inicial (E2), se adaptó el mecanismo de entrega de alertas (que originalmente contemplaba servicios externos como Firebase o SendGrid) hacia un modelo autocontenido en base de datos para garantizar la ejecución determinista en las pruebas automatizadas de integración continua (CI/CD).