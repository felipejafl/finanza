⚡ Pautas y buenas prácticas de Rendimiento en Django
1. Consultas a la base de datos

Evita el clásico N+1 queries usando:

select_related() → para relaciones ForeignKey y OneToOne.

prefetch_related() → para ManyToMany o listas.

# ❌ Mal: cada iteración hace una query extra
for invoice in Invoice.objects.all():
    print(invoice.user.username)

# ✅ Bien: trae la relación en la misma query
for invoice in Invoice.objects.select_related("user"):
    print(invoice.user.username)


Usa only() o defer() para traer solo los campos necesarios.

Aplica índices (db_index=True) en campos usados frecuentemente en filtros y ordenamientos.

2. Paginación

Nunca devuelvas listas enormes.

Usa Paginator en Django o PageNumberPagination en DRF.

from django.core.paginator import Paginator

invoices = Invoice.objects.all()
paginator = Paginator(invoices, 20)  # 20 por página
page = paginator.get_page(1)

3. Cache

Usa caché de consultas, vistas o fragmentos de template.

Backends recomendados: Redis o Memcached.

from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutos
def invoice_list(request):
    ...


Para APIs → caching en capa de servicio (ej. Redis).

4. Uso de señales (signals)

No abuses de post_save/post_delete.

Lógica pesada → mejor colas asíncronas (Celery, RQ).

5. Procesos asíncronos

Django 3+ soporta ASGI y async views.

Para tareas pesadas: usar Celery + Redis/RabbitMQ.

async def async_view(request):
    await asyncio.sleep(1)
    return JsonResponse({"msg": "done"})

6. Templates

Evita lógica compleja en plantillas.

Usa {% cache %} para fragmentos que cambian poco.

{% load cache %}
{% cache 600 sidebar %}
    {% include "includes/sidebar.html" %}
{% endcache %}

7. Archivos estáticos y media

Sirve static y media desde un CDN o Nginx, no desde Django en producción.

Usa collectstatic antes de desplegar.

Optimiza imágenes y activa compresión de assets (con django-compressor, Webpack o Vite).

8. Optimización de consultas complejas

Usa annotate() y aggregate() en lugar de calcular en Python.

from django.db.models import Sum
total = Invoice.objects.aggregate(total=Sum("amount"))["total"]


Evita len(queryset) → usa .count().

Si necesitas SQL avanzado: QuerySet.explain() para revisar planes de ejecución.

9. Sesiones y autenticación

Usa cache-backed sessions (Redis/Memcached) en lugar de BD cuando hay alto tráfico.

Para APIs: usar JWT o tokens en lugar de sesiones persistentes.

10. Despliegue y entorno

Usa Gunicorn/Uvicorn + Nginx.

Configura workers adecuados según CPU (workers = 2 * cores + 1).

Activa GZip o Brotli en Nginx para respuestas grandes.

Usa connection pooling para la base de datos (ej. django-db-geventpool).

11. Monitoreo y métricas

Usa Django Debug Toolbar en desarrollo para detectar consultas innecesarias.

En producción, monitorea con Sentry, New Relic, Prometheus + Grafana.

Loguea tiempos de respuesta y queries lentas.

✅ Resumen rápido

Optimiza queries (select_related, prefetch_related, índices).

Siempre pagina resultados.

Usa caché en múltiples niveles.

Mueve tareas pesadas a Celery.

Sirve estáticos y media con Nginx/CDN.

Monitorea siempre antes de optimizar (¡no optimices a ciegas!).