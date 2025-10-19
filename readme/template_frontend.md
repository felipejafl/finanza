1. Estructura y organización

Usa un directorio global templates/ en la raíz del proyecto.

Cada app con su carpeta de templates dentro:

templates/
│── base.html
│── includes/
│   ├── navbar.html
│   ├── footer.html
│── users/
│   ├── login.html
│   ├── profile.html
│── blog/
│   ├── post_list.html
│   ├── post_detail.html


👉 Evita tener todos los templates en un único nivel, usa carpetas por app.

2. Herencia de plantillas

Usa un layout base (base.html) con {% block content %}.

Extiende en cada template con {% extends "base.html" %}.

<!-- base.html -->
<html>
<head>
  <title>{% block title %}Mi Proyecto{% endblock %}</title>
</head>
<body>
  {% include "includes/navbar.html" %}
  <main>{% block content %}{% endblock %}</main>
  {% include "includes/footer.html" %}
</body>
</html>

3. Includes para componentes

Reutiliza partes comunes (navbar, footer, sidebar).

Guarda en templates/includes/.

{% include "includes/navbar.html" %}

4. Evitar lógica compleja en templates

Mantén las plantillas simples: solo loops, condiciones básicas y filtros.

Cálculos, queries y decisiones → en la vista o servicio.

<!-- ✅ Bien -->
{% for invoice in invoices %}
  <li>{{ invoice.number }} - {{ invoice.total|floatformat:2 }}</li>
{% endfor %}

<!-- ❌ Mal -->
{% if user.invoices.count > 0 and user.balance > 100 and not user.is_suspended %}

5. Filtros y etiquetas personalizadas

Si necesitas lógica más avanzada, crea custom template tags.

# templatetags/currency.py
from django import template

register = template.Library()

@register.filter
def currency(value):
    return f"${value:,.2f}"

{{ invoice.total|currency }}

6. Seguridad en templates

Django escapa HTML automáticamente ({{ variable }}).

Usa |safe solo si confías en el contenido.

Evita pasar datos sensibles directamente al template.

7. Estáticos (CSS, JS, imágenes)

Configura STATIC_URL y STATICFILES_DIRS.

Usa {% load static %} y referencia archivos estáticos así:

<link rel="stylesheet" href="{% static 'css/main.css' %}">
<script src="{% static 'js/app.js' %}"></script>


Para imágenes de usuarios, usa MEDIA_URL.

8. Buenas prácticas de frontend

Usa frameworks CSS (Bootstrap, Tailwind) para acelerar desarrollo.

Usa django-compressor o integraciones con Webpack/Vite si necesitas build de frontend.

Optimiza recursos estáticos en producción con collectstatic + CDN.

9. Internacionalización

Usa {% trans "Texto" %} o gettext_lazy para textos en plantillas.

Mantén locale/ con archivos .po.

<p>{% trans "Bienvenido a la aplicación" %}</p>

10. Templates para emails

Separa templates de correo en templates/emails/.

Usa texto plano + HTML para compatibilidad.

Ejemplo: emails/invoice_paid.html.

💡 Resumen

👉 Los templates deben ser simples, reutilizables y seguros.
👉 Usa herencia, includes, tags personalizados y mantén la lógica en las vistas/servicios, no en HTML.
👉 Organiza bien los recursos estáticos y usa herramientas modernas para frontend si el proyecto lo necesita.