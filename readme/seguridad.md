🛡️ Pautas y buenas prácticas de seguridad en Django
1. Secretos y configuración sensible

Nunca hardcodear SECRET_KEY en el repositorio.

Usar variables de entorno (django-environ, python-decouple).

No exponer credenciales en settings.py ni en logs.

Mantener DEBUG = False en producción ❗.

2. Allowed Hosts

Configurar ALLOWED_HOSTS con los dominios válidos del proyecto.

Ejemplo:

ALLOWED_HOSTS = ["miapp.com", "www.miapp.com"]

3. CSRF Protection

Activada por defecto en Django.

En cada formulario HTML incluir {% csrf_token %}.

Para APIs → usar CSRF_TRUSTED_ORIGINS o tokens seguros.

4. XSS (Cross-Site Scripting)

Django escapa automáticamente las variables en templates ({{ variable }}).

Evitar usar |safe salvo que el contenido sea confiable.

Sanitizar HTML si se permite input enriquecido (bleach, django-bleach).

5. SQL Injection

Usar siempre el ORM de Django.

Evitar concatenar strings en queries crudas.

Si usas raw(), sanitiza parámetros con placeholders.

6. Autenticación y gestión de usuarios

Usa el modelo de usuario personalizado desde el inicio (AUTH_USER_MODEL).

Exigir contraseñas fuertes (AUTH_PASSWORD_VALIDATORS).

Usar LoginRequiredMixin o @login_required en vistas sensibles.

Nunca almacenar contraseñas en texto plano (Django usa PBKDF2 por defecto).

7. Permisos y autorización

Controlar permisos con @permission_required o PermissionRequiredMixin.

Para APIs (DRF), usar permissions.IsAuthenticated, IsAdminUser, o permisos personalizados.

Principio de mínimo privilegio: dar solo los permisos necesarios.

8. Seguridad en cookies y sesiones

Configurar en producción:

SESSION_COOKIE_SECURE = True     # solo por HTTPS  
CSRF_COOKIE_SECURE = True        # solo por HTTPS  
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  
SESSION_COOKIE_HTTPONLY = True   # no accesible por JS  


Usar signed cookies para datos sensibles.

9. HTTPS

Forzar HTTPS con:

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


Instalar certificados válidos (ej. Let’s Encrypt).

10. Headers de seguridad

Configurar en settings.py o via Nginx:

X_FRAME_OPTIONS = "DENY" (previene clickjacking).

SECURE_BROWSER_XSS_FILTER = True.

SECURE_CONTENT_TYPE_NOSNIFF = True.

Referrer-Policy: same-origin.

Content-Security-Policy (CSP) para limitar scripts.

11. Archivos estáticos y media

No servir MEDIA_URL directamente sin control de permisos si los archivos son sensibles.

Servir estáticos con Nginx/Apache, no desde Django en producción.

Validar extensiones MIME de archivos subidos.

12. Protección contra ataques comunes

Brute-force login → usar django-axes o throttling en DRF.

Rate limiting para APIs (django-ratelimit).

CORS seguro → restringir orígenes con django-cors-headers.

13. Logging y monitoreo

Configurar LOGGING en settings.py para guardar errores.

Usar Sentry o Rollbar para capturar excepciones en producción.

Revisar logs de acceso (Nginx/Gunicorn).

14. Actualizaciones

Mantener Django y librerías siempre actualizadas.

Suscribirse a Django security releases
.

✅ Resumen

Secretos fuera del repo.

DEBUG = False en producción.

CSRF y validación activa siempre.

Cookies seguras + HTTPS obligatorio.

ORM para queries (evitar SQL injection).

Permisos estrictos, sesiones seguras y headers configurados.

Monitoreo y actualizaciones constantes.