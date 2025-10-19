🧪 Pautas y prácticas recomendadas en Pruebas (Testing) en Django
1. Herramientas recomendadas

Usa pytest + pytest-django en lugar del unittest estándar.

Sintaxis más limpia.

Fixtures reutilizables.

Mejor output de errores.

Usa factory_boy o model_bakery para crear datos de prueba.

2. Organización

Carpeta tests/ en cada app:

app_name/
│── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   ├── test_serializers.py


Tests globales en project_root/tests/.

Nombres descriptivos: test_invoice_creation_success, no test1.

3. Tipos de tests

Unit tests:

Prueban funciones/métodos individuales.

Sin tocar la base de datos si es posible.

Integration tests:

Validan interacción entre modelos, servicios y vistas.

Functional tests:

Usan client de Django o APIClient de DRF.

Simulan requests reales.

End-to-End (E2E) (opcional):

Selenium, Playwright o Cypress.

Simulan al usuario en navegador.

4. Pruebas de modelos

Verificar __str__.

Validaciones (clean, validators).

Constraints (unicidad, integridad).

def test_invoice_str():
    invoice = Invoice.objects.create(number="INV-001", total=100)
    assert str(invoice) == "Invoice INV-001"

5. Pruebas de vistas / controladores

Usar client para simular requests.

Verificar códigos de estado (200, 302, 403, 404).

Validar contenido esperado en la respuesta.

def test_invoice_list_view(client, user, invoice):
    client.force_login(user)
    response = client.get("/invoices/")
    assert response.status_code == 200
    assert invoice.number in response.content.decode()

6. Pruebas de formularios

Validar que campos obligatorios y reglas funcionen.

def test_invoice_form_invalid_total():
    form = InvoiceForm(data={"number": "INV-001", "total": -10})
    assert not form.is_valid()
    assert "El total debe ser mayor a 0." in form.errors["total"]

7. Pruebas de APIs (con DRF)

Usar APIClient en lugar de client.

Validar autenticación, permisos y payloads.

from rest_framework.test import APIClient

def test_api_invoice_list(user, invoice):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/invoices/")
    assert response.status_code == 200
    assert invoice.number in [inv["number"] for inv in response.json()]

8. Fixtures y datos de prueba

Evitar fixtures.json estáticos → usar factories dinámicas.

Ejemplo con model_bakery:

from model_bakery import baker

def test_invoice_created_with_factory():
    invoice = baker.make("billing.Invoice", total=150)
    assert invoice.total == 150

9. Cobertura

Usar pytest --cov para medir cobertura.

Meta: 70–90%, pero priorizando código crítico (validaciones, seguridad, pagos).

10. Automatización

Ejecutar tests en CI/CD (GitHub Actions, GitLab CI, etc.).

Prevenir merges si los tests fallan.

✅ Resumen

Usa pytest + pytest-django + factory_boy/model_bakery.

Organiza tests por tipo (test_models.py, test_views.py, etc.).

Cubre modelos, vistas, formularios, APIs y permisos.

Mantén tests rápidos, claros y automáticos en CI/CD.