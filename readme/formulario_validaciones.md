1. Usa ModelForm cuando aplique

Para CRUD directo sobre modelos.

Se ahorra código repetido (campos + validaciones de modelo).

Úsalo para crear/editar objetos comunes.

from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["number", "total", "due_date"]

2. Usa Form para lógica no directamente ligada a un modelo

Ideal para formularios de login, búsqueda, filtros, contacto.

class ContactForm(forms.Form):
    name = forms.CharField(max_length=50)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

3. Validaciones: dónde hacerlas

En el modelo: reglas de negocio globales (unique, validators, clean).

En el formulario: validaciones específicas de ese caso de uso (clean_<field>(), clean()).

En el serializer (DRF): validaciones para APIs.

👉 Regla práctica:

Si es una regla que siempre debe cumplirse → modelo.

Si es solo para un formulario concreto → formulario.

4. Validación en campos individuales
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["number", "total"]

    def clean_total(self):
        total = self.cleaned_data["total"]
        if total <= 0:
            raise forms.ValidationError("El total debe ser mayor a 0.")
        return total

5. Validación cruzada (entre campos)
class RegisterForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Las contraseñas no coinciden.")

6. Widgets y usabilidad

Usa widgets para personalizar inputs (DateInput, PasswordInput).

Usa librerías como django-crispy-forms o widget-tweaks para integrar Bootstrap/Tailwind fácilmente.

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

7. Errores claros

Muestra mensajes de error en templates ({{ form.errors }}).

Personaliza error_messages por campo:

class InvoiceForm(forms.ModelForm):
    number = forms.CharField(
        max_length=20,
        error_messages={"unique": "Ya existe una factura con este número."}
    )
    class Meta:
        model = Invoice
        fields = ["number", "total"]

8. Seguridad

Siempre incluye {% csrf_token %} en formularios HTML.

Escapa inputs de usuario (Django ya lo hace en templates).

Nunca confíes en validación solo en frontend (usa JS solo como mejora UX, no seguridad).

9. Formsets y modelformsets

Úsalos para manejar múltiples formularios a la vez.

Ejemplo: cargar varias facturas en un solo submit.

from django.forms import modelformset_factory
InvoiceFormSet = modelformset_factory(Invoice, fields=("number", "total"), extra=3)

10. Tests de formularios

Prueba que la validación funciona:

def test_invoice_form_invalid_total():
    form = InvoiceForm(data={"number": "A-001", "total": -50})
    assert not form.is_valid()
    assert "El total debe ser mayor a 0." in form.errors["total"]

💡 Resumen

👉 Usa ModelForm para CRUD de modelos, Form para lógica independiente.
👉 Valida lo global en modelos, lo contextual en formularios.
👉 Usa widgets y librerías para mejor UX.
👉 Siempre maneja errores y seguridad (csrf, escapes, tests).