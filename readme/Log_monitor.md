📊 Pautas y buenas prácticas en Logging y Monitoreo en Django
1. Principios generales

Registrar todo lo necesario, pero sin ruido (evitar saturar logs).

Diferenciar niveles de severidad:

DEBUG: detalles técnicos (solo en dev).

INFO: eventos importantes del flujo normal.

WARNING: situaciones anómalas pero no críticas.

ERROR: errores que no interrumpen el sistema.

CRITICAL: errores graves que requieren acción inmediata.

Centralizar logs (no dejarlos solo en archivos locales).

2. Configuración de Logging en Django

En settings.py se recomienda definir una configuración robusta:

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "/var/log/django/app.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "myapp": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


👉 Esto permite logs distintos para Django core y tu aplicación.

3. Buenas prácticas de Logging

Usa el módulo logging en lugar de print().

import logging

logger = logging.getLogger(__name__)

def process_invoice(invoice):
    logger.info(f"Procesando factura {invoice.id}")
    try:
        # lógica
        logger.debug("Detalle técnico...")
    except Exception as e:
        logger.error(f"Error al procesar factura {invoice.id}: {e}", exc_info=True)


Nunca loguear información sensible (contraseñas, tokens, tarjetas).

Mantener logs en formato estructurado JSON si se usarán en sistemas externos (ej. ELK, Graylog).

4. Monitoreo en tiempo real

Integrar con Sentry, Rollbar o Airbrake → para capturar excepciones en producción con contexto (usuario, request, stack trace).

Configurar alertas (Slack, correo, PagerDuty).

5. Métricas y performance

Usar Prometheus + Grafana para métricas de performance:

Latencia de requests.

Cantidad de queries.

Errores por minuto.

Middleware útil: django-prometheus.

6. Auditoría

Registrar acciones de usuarios en logs de auditoría:

Inicios de sesión / intentos fallidos.

Cambios en modelos críticos.

Acceso a datos sensibles.

Se puede implementar con signals (post_save, post_delete).

7. Infraestructura de Logs

En producción → no dejar logs solo en archivos.

Opciones recomendadas:

ELK (Elasticsearch + Logstash + Kibana).

Graylog.

Papertrail o LogDNA.

Cloud Logging (AWS CloudWatch, GCP Stackdriver, Azure Monitor).

8. Health Checks

Implementar un endpoint /health/ protegido para monitoreo externo.

Validar: DB, cache, workers, colas de tareas.

Herramientas: django-health-check.

✅ Resumen

Configura logging con diferentes niveles (DEBUG, INFO, WARNING, ERROR).

Usa handlers múltiples (consola + archivo + servicio externo).

Nunca loguees información sensible.

Integra con Sentry para errores y Prometheus + Grafana para métricas.

Usa logs JSON estructurados si centralizas en ELK.

Implementa health checks y auditoría para seguridad.