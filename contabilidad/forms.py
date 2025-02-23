from datetime import date
from django import forms
from .models import Cuenta, Categoria, Presupuesto, Transaccion, TicketImagen
  
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
        fields = ['categoria', 'tipo', 'importe']

class TicketImagenForm(forms.ModelForm):
    class Meta:
        model = TicketImagen
        fields = ['imagen']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
class TransaccionFilterForm(forms.Form):
    fecha_inicio = forms.DateField(
        label='Fecha de Inicio',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    fecha_fin = forms.DateField(
        label='Fecha de Fin',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    categorias = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.all(),
        label='Categorías',
        required=False,
        widget=forms.SelectMultiple # Cambiado a SelectMultiple
    )
    cuentas = forms.ModelMultipleChoiceField(
        queryset=Cuenta.objects.all(),
        label='Cuentas',
        required=False,
        widget=forms.SelectMultiple # Cambiado a SelectMultiple
    )
    tipo_cuenta = forms.ChoiceField(
        choices=[('', '---------'), ('ingreso', 'Ingreso'), ('gasto', 'Gasto')],
        label='Tipo de Cuenta',
        required=False,
        initial=''
    )
    descripcion_palabra_clave = forms.CharField(
        label='Palabra Clave en Descripción',
        required=False
    )