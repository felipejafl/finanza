1. Elegir entre FBV y CBV

FBV (Function-Based Views):

✅ Úsalas para vistas muy simples (ej: un "ping", un hello world).

❌ Evítalas en lógica compleja.

CBV (Class-Based Views):

✅ Recomendadas para la mayoría de casos.

Reutilizables, extensibles y organizadas.

Usa las genéricas (ListView, DetailView, CreateView, UpdateView, DeleteView).

💡 Regla práctica: si la vista hace más que un render simple → usa CBV.

2. Mantener vistas delgadas

Las vistas deben:

Recibir la request.

Delegar la lógica al servicio/manager/serializer.

Devolver una response.

👉 Nunca metas cálculos complejos, queries repetidas o reglas de negocio dentro de la vista.

# ❌ Mal
def pay_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.is_paid = True
    invoice.save()
    send_email(invoice.user.email, "Factura pagada")
    return JsonResponse({"status": "ok"})

# ✅ Bien: delegar en servicios
from .services import pay_invoice_service

def pay_invoice(request, pk):
    invoice = pay_invoice_service(pk)
    return JsonResponse({"status": "ok", "invoice": invoice.number})

3. URLs limpias

Usa urls.py en cada app.

Namespaces para evitar conflictos (app_name = "billing").

Evita parámetros raros:

✅ /invoices/123/pay/

❌ /do_action?id=123&type=invoice&pay=true

4. Uso de mixins

Para CBV, aprovecha mixins (LoginRequiredMixin, PermissionRequiredMixin).

Crea mixins propios para lógica repetida.

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Invoice

class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    paginate_by = 20

5. Serialización y APIs

Para APIs, usa Django REST Framework (DRF).

Organiza en viewsets.py, serializers.py, urls.py.

Usa ModelViewSet cuando aplique (CRUD rápido).

from rest_framework.viewsets import ModelViewSet
from .models import Invoice
from .serializers import InvoiceSerializer

class InvoiceViewSet(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

6. Autenticación y permisos

Usa decoradores como @login_required, @permission_required.

En CBV: LoginRequiredMixin, PermissionRequiredMixin.

En DRF: permission_classes y authentication_classes.

7. Respuestas

Para HTML: render(request, "template.html", context).

Para JSON: usa JsonResponse o DRF (Response).

Nunca devuelvas datos sensibles directamente.

8. Optimización de consultas

Prefetch en la vista antes de pasar al template:

class InvoiceListView(ListView):
    model = Invoice

    def get_queryset(self):
        return Invoice.objects.select_related("user").all()

9. Tests de vistas

Prueba tanto la respuesta (200, 302, 403) como el contenido.

Usa pytest-django con client.

def test_invoice_list_view(client, user, invoice):
    client.force_login(user)
    response = client.get("/invoices/")
    assert response.status_code == 200
    assert invoice.number in response.content.decode()

10. Buenas prácticas extra

Usa paginación en listas largas (ListView, PageNumberPagination).

Mantén vistas cortas (<40 líneas).

Documenta qué hace cada vista.

Centraliza lógica en services.py y managers.py.

💡 Resumen:
👉 Las vistas deben ser delgadas, enfocadas en orquestar flujo, no en hacer el trabajo duro. Para eso están los services, managers, serializers y templates.