🔨🤖🔧 Pautas Generales de Desarrollo en Django
1. Estructura y Organización del Proyecto

Usa django-admin startproject y startapp (evita meter todo en una sola app).
Agrupa apps por dominio funcional (ej: users, billing, blog) y no por capas (ej: models, views, etc.).
Mantén los settings desacoplados por entorno: settings/base.py, settings/dev.py, settings/prod.py.
Configura rutas con namespace en urls.py para evitar colisiones (app_name = "blog").

2. Modelos y Base de Datos

Usa nombres descriptivos para modelos y campos.
Implementa __str__ en todos los modelos.
Normaliza relaciones: ForeignKey, ManyToManyField, OneToOneField.
Define related_name siempre en relaciones.
Evita lógica de negocio en models.py -> usa managers o services.
Aplica migraciones pequeñas y frecuentes (makemigrations, migrate).

3. Vistas y Controladores

Usa Class-Based Views (CBV) siempre que sea posible en lugar de funciones.
Para APIs: usa Django REST Framework (DRF) con ViewSets + Routers.
No sobrecargues las vistas: lógica compleja ➝ services o utils.

4. Templates y Frontend

Sigue la filosofía Django template language (DTL) para lógica mínima.
Evita lógica compleja en plantillas: cálculos ➝ en la vista.
Usa base.html con template inheritance.
Escapa siempre las variables ({{ variable }} ya lo hace por defecto).

5. Formularios y Validación

Usa ModelForm cuando aplique.
Aplica validaciones en el modelo (clean, validators) y no solo en el formulario.
Personaliza widgets para mejorar UX.
Usa crispy-forms o django-widget-tweaks para estilos.

6. Seguridad

Nunca subas SECRET_KEY al repo (usa variables de entorno).
Activa SECURE_SSL_REDIRECT = True en producción.
Usa CSRF en todos los formularios ({% csrf_token %}).
Configura ALLOWED_HOSTS correctamente.
Escapa siempre input de usuario.
Configura X_FRAME_OPTIONS, SECURE_HSTS_SECONDS, SECURE_COOKIES.

7. Pruebas (Testing)

Usa pytest + pytest-django (más flexible que unittest).
Prueba modelos, vistas, APIs y templates.
Cubre validaciones y edge cases.
Automatiza pruebas en CI/CD.

8. Rendimiento

Usa select_related y prefetch_related para evitar N+1 queries.
Cachea consultas costosas (django-redis).
Usa paginación en listas grandes.
Mantén las consultas en Django ORM, evita SQL crudo salvo necesidad.

9. Estilo de Código

Sigue PEP8 (usa black + isort + flake8).
Documenta clases y métodos.
Usa nombres descriptivos (no x, obj, data).
Mantén archivos cortos (<300 líneas).

10. Despliegue

Usa Gunicorn/Uvicorn + Nginx.
Configura ASGI para soportar WebSockets.
Usa Docker para entornos consistentes.
Configura CI/CD con GitHub Actions/GitLab CI.
Monitorea con Sentry, Prometheus o similar.

11. Internacionalización

Usa ugettext_lazy (gettext_lazy) para cadenas traducibles.
Separa archivos de idioma (locale).

12. Logging y Monitoreo

Configura LOGGING en settings.py.
Guarda logs en archivo + servicio externo (ej: ELK stack).
Notificaciones de errores: Sentry.