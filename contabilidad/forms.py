from datetime import date
from django import forms
from .models import Cuenta, Categoria, Presupuesto, Transaccion

class UploadFileForm(forms.Form):
    file = forms.field = 'ruta'
    
class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['nombre', 'tipo', 'saldo']

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']

class TransaccionForm(forms.ModelForm):
    cuenta = forms.ModelChoiceField(queryset=Cuenta.objects.all(), label='Cuenta')
    fecha = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control',
                'value': date.today().strftime('%Y-%m-%d')
            }), label='Fecha')
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), required=False, label='Categoría')
    importe = forms.DecimalField(label='Importe')
    descripcion = forms.CharField(label='Descripción')
    
    class Meta:
        model = Transaccion
        fields = ['cuenta','fecha', 'categoria', 'importe', 'descripcion' ]

class PresupuestoForm(forms.ModelForm):
    importe = forms.DecimalField(label='Importe')
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), required=False, label='Categoría')

    class Meta:
        model = Presupuesto
        fields = ['categoria', 'importe']