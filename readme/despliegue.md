🚀 Pautas y buenas prácticas de Despliegue en Django
1. Configuración del proyecto

DEBUG = False siempre en producción.

Configurar ALLOWED_HOSTS con tus dominios.

Mover credenciales y claves a variables de entorno (django-environ, python-decouple).

Usar configuración modular: settings/base.py, settings/dev.py, settings/prod.py.

2. Servidor de aplicaciones

Django no debe correrse con runserver en producción.

Usar un WSGI/ASGI server:

Gunicorn (WSGI).

Uvicorn o Hypercorn (ASGI, ideal si usas websockets o async).

Colocar un Nginx o Apache como reverse proxy delante de Gunicorn/Uvicorn.

Ejemplo (Gunicorn):

gunicorn project_name.wsgi:application --workers 3 --bind 0.0.0.0:8000

3. Base de datos

Usar PostgreSQL en producción (no SQLite).

Configurar pool de conexiones (django-db-geventpool, pgbouncer).

Ejecutar siempre migraciones en despliegues (python manage.py migrate).

Activar backups automáticos y monitoreo.

4. Archivos estáticos y media

Ejecutar:

python manage.py collectstatic


Servir estáticos y media desde:

Nginx directamente.

O mejor aún, un CDN (CloudFront, Cloudflare, etc.).

Optimizar imágenes y activar compresión de assets.

5. Seguridad

Configurar en settings.py:

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True


Usar HTTPS obligatorio (certificados con Let’s Encrypt).

Rotar claves y tokens regularmente.

6. Procesos en segundo plano

Tareas pesadas → mover a un task queue:

Celery + Redis/RabbitMQ.

Django-Q o Huey como alternativas.

Configurar workers y monitorearlos con supervisor o systemd.

7. Cache

Configurar un backend de caché: Redis o Memcached.

Usar caché por:

Vista (@cache_page).

Fragmento de template ({% cache %}).

Capa de queries.

8. Logs y monitoreo

Configurar LOGGING en settings.py para guardar errores en archivo o en un servicio centralizado.

Usar herramientas de monitoreo:

Sentry → errores.

Prometheus + Grafana → métricas.

ELK stack → logs centralizados.

9. Automatización y CI/CD

Usar GitHub Actions / GitLab CI / Jenkins para:

Ejecutar tests antes del despliegue.

Desplegar automáticamente a staging/producción.

Usar Docker para entornos reproducibles.

Infraestructura como código (Terraform, Ansible).

10. Escalabilidad

Escalar horizontalmente con Docker + Kubernetes o ECS/EKS.

Balanceo de carga con Nginx, HAProxy o ELB (AWS).

Separar servicios:

BD en su propio servidor/servicio (RDS).

Cache en instancia separada (Redis/Memcached).

✅ Resumen

Nunca runserver en producción → usar Gunicorn/Uvicorn + Nginx.

PostgreSQL con pooling.

Static & media en CDN/Nginx.

HTTPS obligatorio + headers de seguridad.

Celery para tareas pesadas.

CI/CD + Docker + monitoreo.

Logs centralizados y backups automáticos.