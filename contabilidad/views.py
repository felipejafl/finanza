from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from .forms import UploadFileForm  # Formulario para subir archivos
from .tasks import importar_transacciones  # Tarea Celery para importar (opcional)
from .models import Cuenta, Transaccion, Categoria, Presupuesto
from django.db.models import Sum
from django.contrib import messages
from .forms import CuentaForm, PresupuestoForm, CategoriaForm, TransaccionForm
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def inicio(request):
    return render(request, 'contabilidad/index.html')

def cuenta_listar(request):
     cuentas = Cuenta.objects.all()
     context = {
         'cuentas': cuentas,
     }
     return render(request, 'contabilidad/cuentas/listar.html', context)

def cuenta_crear(request):
    if request.method == 'POST':
        form = CuentaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada correctamente.')
            return redirect('cuenta_listar')
    else:
        form = CuentaForm()

    return render(request, 'contabilidad/cuentas/crear.html', {'form': form})

def cuenta_editar(request, pk):
    cuenta = get_object_or_404(Cuenta, pk=pk)
    if request.method == 'POST':
        form = CuentaForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta editada correctamente.')
            return redirect('cuenta_listar')
    else:
        form = CuentaForm(instance=cuenta)

    context = {
        'form': form,
    }
    return render(request, 'contabilidad/cuentas/editar.html', context)

def cuenta_eliminar(request, pk):
    cuenta = get_object_or_404(Cuenta, pk=pk)
    cuenta.delete()
    messages.success(request, 'Cuenta eliminada correctamente.')
    return redirect('cuenta_listar')

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TransaccionSerializer

class TransaccionListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        transacciones = Transaccion.objects.select_related('categoria', 'cuenta')
        serializer = TransaccionSerializer(transacciones, many=True)
        return Response(serializer.data)

def transaccion_listar(request):
    return render(request, 'contabilidad/transacciones/listar.html')
  
def transaccion_crear(request):
    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transacción creada correctamente.')
            return redirect('transaccion_listar')
    else:
        form = TransaccionForm()

    context = {
        'form': form,
    }
    return render(request, 'contabilidad/transacciones/crear.html', context)

def transaccion_editar(request, pk):
    transaccion = get_object_or_404(Transaccion, pk=pk)
    if request.method == 'POST':
        form = TransaccionForm(request.POST, instance=transaccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transacción editada correctamente.')
            return redirect('transaccion_listar')
    else:
        form = TransaccionForm(instance=transaccion)

    context = {
        'form': form,
    }
    return render(request, 'contabilidad/transacciones/editar.html', context)

def transaccion_eliminar(request, pk):
    transaccion = get_object_or_404(Transaccion, pk=pk)
    transaccion.delete()
    messages.success(request, 'Transacción eliminada correctamente.')
    return redirect('transaccion_listar')

def presupuesto_listar(request):
    presupuestos = Presupuesto.objects.all()
    total = presupuestos.aggregate(Sum('importe'))['importe__sum']
    context = {
        'presupuestos': presupuestos,
        'total': total,
    }
    return render(request, 'contabilidad/presupuestos/listar.html', context)

def presupuesto_crear(request):
    if request.method == 'POST':
        form = PresupuestoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Presupuesto creada correctamente.')
            return redirect('presupuesto_listar')
    else:
        form = PresupuestoForm()

    context = {
        'form': form,
    }
    return render(request, 'contabilidad/presupuestos/crear.html', context)

def presupuesto_editar(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    if request.method == 'POST':
        form = PresupuestoForm(request.POST, instance=presupuesto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Presupuesto editada correctamente.')
            return redirect('presupuesto_listar')
    else:
        form = PresupuestoForm(instance=presupuesto)

    context = {
        'form': form,
    }
    return render(request, 'contabilidad/presupuestos/editar.html', context)

def presupuesto_eliminar(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    presupuesto.delete()
    messages.success(request, 'Presupuesto eliminada correctamente.')
    return redirect('presupuesto_listar')


def categoria_listar(request):
    categorias = Categoria.objects.all()
    context = {
        'categorias': categorias,
    }
    return render(request, 'contabilidad/categorias/listar.html', context)

def categoria_crear(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('categoria_listar')
    else:
        form = CategoriaForm()

    context = {
        'form': form,
    }
    return render(request, 'contabilidad/categorias/crear.html', context)

def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría editada correctamente.')
            return redirect('categoria_listar')
    else:
        form = CategoriaForm(instance=categoria)

    context = {
        'form': form,
    }
    return render(request, 'contabilidad/categorias/editar.html', context)

def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.delete()
    messages.success(request, 'Categoría eliminada correctamente.')
    return redirect('categoria_listar')

#Reportes
def reporte_balance_general(request):
    # Calcular saldos de Keily
    cuentas_keily = Cuenta.objects.all().annotate(importe=Sum('transaccion_Keily_Ing') - Sum('transaccion_Keily_Gas'))
    # Calcular saldos de JOSE
    cuentas_jose = Cuenta.objects.all().annotate(importe=Sum('transaccion_Jose_Ing') - Sum('transaccion_Jose_Gas'))
    # Saldo Total
    total_cuentas= cuentas_keily + cuentas_jose
    
    context = {
        'keily': cuentas_keily,
        'Jose': cuentas_jose,
        'Total': total_cuentas,
    }
    return render(request, 'contabilidad/reportes/balance_general.html', context)

def reporte_estado_resultados(request):
    # Calcular ingresos
    ingresos = Transaccion.objects.filter(tipo=Transaccion.TIPO_INGRESO).aggregate(total=Sum('importe'))
    total_ingresos = ingresos['total'] or 0

    # Calcular gastos
    gastos = Transaccion.objects.filter(tipo=Transaccion.TIPO_GASTO).aggregate(total=Sum('importe'))
    total_gastos = gastos['total'] or 0

    # Calcular utilidad neta
    utilidad_neta = total_ingresos - total_gastos

    context = {
        'ingresos': ingresos,
        'total_ingresos': total_ingresos,
        'gastos': gastos,
        'total_gastos': total_gastos,
        'utilidad_neta': utilidad_neta,
    }
    return render(request, 'contabilidad/reportes/estado_resultados.html', context)

def reporte_mayor_cuentas(request):
    # Obtener movimientos de todas las cuentas
    movimientos = Transaccion.objects.select_related('cuenta_acreedora', 'cuenta_deudora').order_by('fecha')

    context = {
        'movimientos': movimientos,
    }
    return render(request, 'contabilidad/reportes/mayor_cuentas.html', context)

def reporte_libro_diario(request):
    # Obtener asientos de todas las transacciones
    asientos = Transaccion.objects.select_related('cuenta_acreedora', 'cuenta_deudora').order_by('fecha')

    context = {
        'asientos': asientos,
    }
    return render(request, 'contabilidad/reportes/libro_diario.html', context)

from .importarDB import importar_transacciones  # Función de importación
def importar_datos(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST)
        if form.is_valid():
            importar_transacciones('D:\\Jose\\Documents\\Desarrollo\\Finanzas\\finanza\\contabilidad\\db.xlsx')
            return HttpResponse('Archivo subido correctamente')
    else:
        form = UploadFileForm()
    return render(request, 'contabilidad/transacciones/importar.html', {'form': form})

