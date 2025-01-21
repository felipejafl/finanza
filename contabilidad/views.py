from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from .forms import UploadFileForm  # Formulario para subir archivos
from .tasks import importar_transacciones  # Tarea Celery para importar (opcional)
from .models import Cuenta, Transaccion, Categoria, Presupuesto
from django.db.models import Sum
from datetime import datetime
from datetime import date
from django.db.models.functions import TruncMonth, TruncYear
from django.contrib import messages
from .forms import CuentaForm, PresupuestoForm, CategoriaForm, TransaccionForm


# Create your views here.
def inicio(request):
    # Fecha actual
    MESES = {
        1: 'Enero',
        2: 'Febrero',
        3: 'Marzo',
        4: 'Abril', 
        5: 'Mayo',
        6: 'Junio',
        7: 'Julio',
        8: 'Agosto',
        9: 'Septiembre',
        10: 'Octubre',
        11: 'Noviembre',
        12: 'Diciembre'
    }
    hoy = date.today()
    mes_actual = MESES[hoy.month]
    año_actual = hoy.year

    cuentas = Cuenta.objects.filter(tipo='ingreso')
    saldo_ingresos = cuentas.aggregate(saldo_total=Sum('saldo'))['saldo_total'] or 0
    ingresos_totales = calcular_ingresos(anio=datetime.now().year) + saldo_ingresos
    ingreso_mes = calcular_ingresos(mes=datetime.now().month, anio=datetime.now().year) 
    gastos_totales = calcular_gastos(anio=datetime.now().year)
    gastos_mes = calcular_gastos(mes=datetime.now().month, anio=datetime.now().year)
    beneficio_total = calcular_beneficio(anio=datetime.now().year) + saldo_ingresos
    beneficio_mes = calcular_beneficio(mes=datetime.now().month, anio=datetime.now().year)
    presupuesto_salario = Presupuesto.objects.filter(categoria__nombre='Salario').aggregate(Sum('importe'))['importe__sum']
    presupuesto_otros = Presupuesto.objects.exclude(categoria__nombre='Salario').aggregate(Sum('importe'))['importe__sum']
    presupuesto_beneficio = presupuesto_salario - presupuesto_otros
    importes_por_categoria = calcular_importes_por_categoria(mes=datetime.now().month, anio=datetime.now().year)
    context = {
        'ingresos_totales': ingresos_totales,
        'gastos_totales': gastos_totales,
        'beneficio_total': beneficio_total,
        'ingreso_mes': ingreso_mes,
        'gastos_mes': gastos_mes,
        'beneficio_mes': beneficio_mes,
        'presupuesto_salario': presupuesto_salario,
        'presupuesto_otros': presupuesto_otros,
        'presupuesto_beneficio': presupuesto_beneficio,
        'importes_por_categoria': importes_por_categoria,
        'mes_actual': mes_actual,
    }
    datojs = {
        

    }
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(datojs)
    else:
        return render(request, 'contabilidad/index.html', context)

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
    # Obtener todos los presupuestos
    presupuestos = Presupuesto.objects.all()

    # Obtener la suma de los importes de la categoría "Salario"
    salario = presupuestos.filter(categoria__nombre='Salario').aggregate(Sum('importe'))['importe__sum']
    salario_importe = salario if salario else 0

    # Calcular la suma de todas las demás categorías excluyendo "Salario"
    total_otros = presupuestos.exclude(categoria__nombre='Salario').aggregate(Sum('importe'))['importe__sum']
    total_otros = total_otros if total_otros else 0

    # Calcular el total final
    total = total_otros - salario_importe

    # Contexto para la plantilla
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

def reporte_presupuesto_mensual(request):
    # Obtener mes y año actual por defecto
    hoy = date.today()
    mes_actual = int(request.GET.get('mes', hoy.month))  # Mes seleccionado o actual
    año_actual = int(request.GET.get('año', hoy.year))  # Año seleccionado o actual

    # Obtener el presupuesto anual por categoría
    presupuestos = Presupuesto.objects.all()

    # Preparar los datos del reporte
    reporte = []
    for presupuesto in presupuestos:
        # Calcular presupuesto mensual
        presupuesto_mensual = presupuesto.importe / 12

        # Calcular la ejecución real (transacciones realizadas en el mes y año seleccionados)
        ejecucion_real = Transaccion.objects.filter(
            categoria=presupuesto.categoria,
            fecha__year=año_actual,
            fecha__month=mes_actual
        ).aggregate(total=Sum('importe'))['total'] or 0

        # Calcular la variación (presupuesto mensual - ejecución real)
        variacion = presupuesto_mensual - ejecucion_real

        # Calcular porcentaje de ejecución
        porcentaje_ejecucion = (ejecucion_real / presupuesto_mensual * 100) if presupuesto_mensual > 0 else 0

        # Agregar datos al reporte
        reporte.append({
            'categoria': presupuesto.categoria.nombre,
            'presupuesto_anual': presupuesto.importe,
            'presupuesto_mensual': presupuesto_mensual,
            'ejecucion_real': ejecucion_real,
            'variacion': variacion,
            'porcentaje_ejecucion': porcentaje_ejecucion,
        })

    context = {
        'reporte': reporte,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'meses': range(1, 12),  # Lista de meses (1-12)
        'años': range(hoy.year - 5, hoy.year + 1),  # Últimos 5 años
    }
    return render(request, 'contabilidad/reportes/presupuesto_mensual.html', context)


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
    # Calcular ingresos totales
    cuentas_ingreso = Cuenta.objects.filter(tipo='ingreso')
    saldo_ingresos = cuentas_ingreso.aggregate(saldo_total=Sum('saldo'))['saldo_total'] or 0
    transacciones_ingresos = Transaccion.objects.filter(cuenta__tipo='ingreso').aggregate(total=Sum('importe'))['total'] or 0
    total_ingresos = saldo_ingresos + transacciones_ingresos

    # Calcular gastos totales
    cuentas_gasto = Cuenta.objects.filter(tipo='gasto')
    saldo_gastos = cuentas_gasto.aggregate(saldo_total=Sum('saldo'))['saldo_total'] or 0
    transacciones_gastos = Transaccion.objects.filter(cuenta__tipo='gasto').aggregate(total=Sum('importe'))['total'] or 0
    total_gastos = saldo_gastos + transacciones_gastos

    # Balance final (ingresos - gastos)
    balance_total = total_ingresos - total_gastos

    context = {
        'saldo_ingresos': saldo_ingresos,
        'transacciones_ingresos': transacciones_ingresos,
        'total_ingresos': total_ingresos,
        'saldo_gastos': saldo_gastos,
        'transacciones_gastos': transacciones_gastos,
        'total_gastos': total_gastos,
        'balance_total': balance_total,
    }
    return render(request, 'contabilidad/reportes/balance_general.html', context)

def reporte_estado_resultados(request):
    # Calcular ingresos
    cuentas_ingreso = Cuenta.objects.filter(tipo='ingreso')
    saldo_ingresos = cuentas_ingreso.aggregate(saldo_total=Sum('saldo'))['saldo_total'] or 0
    transacciones_ingresos = Transaccion.objects.filter(cuenta__tipo='ingreso').aggregate(total=Sum('importe'))['total'] or 0
    total_ingresos = saldo_ingresos + transacciones_ingresos

    # Calcular gastos
    cuentas_gasto = Cuenta.objects.filter(tipo='gasto')
    saldo_gastos = cuentas_gasto.aggregate(saldo_total=Sum('saldo'))['saldo_total'] or 0
    transacciones_gastos = Transaccion.objects.filter(cuenta__tipo='gasto').aggregate(total=Sum('importe'))['total'] or 0
    total_gastos = saldo_gastos + transacciones_gastos

    # Calcular utilidad neta
    utilidad_neta = total_ingresos - total_gastos

    context = {
        'saldo_ingresos': saldo_ingresos,
        'transacciones_ingresos': transacciones_ingresos,
        'total_ingresos': total_ingresos,
        'saldo_gastos': saldo_gastos,
        'transacciones_gastos': transacciones_gastos,
        'total_gastos': total_gastos,
        'utilidad_neta': utilidad_neta,
    }
    return render(request, 'contabilidad/reportes/estado_resultados.html', context)

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

# 1. Ingreso mensual o total
def calcular_ingresos(mes=None, anio=None):
    """Calcula los ingresos totales o mensuales basados en las transacciones de cuentas de ingreso."""
    filtro = {'cuenta__tipo': 'ingreso'}  # Filtrar solo cuentas de tipo ingreso
    if mes and anio:
        filtro.update({'fecha__month': mes, 'fecha__year': anio})
    elif anio:
        filtro.update({'fecha__year': anio})
    
    total_ingresos = Transaccion.objects.filter(**filtro).aggregate(total=Sum('importe'))['total'] or 0
    return total_ingresos

# 2. Gastos mensual o total
def calcular_gastos(mes=None, anio=None):
    """Calcula los gastos totales o mensuales basados en las transacciones de cuentas de gasto."""
    filtro = {'cuenta__tipo': 'gasto'}  # Filtrar solo cuentas de tipo gasto
    
    if mes and anio:
        filtro.update({'fecha__month': mes, 'fecha__year': anio})
    elif anio:
        filtro.update({'fecha__year': anio})
    
    total_gastos = Transaccion.objects.filter(**filtro).aggregate(total=Sum('importe'))['total'] or 0
    return total_gastos

# 3. Beneficio mensual o total
def calcular_beneficio(mes=None, anio=None):
    """Calcula el beneficio como la diferencia entre ingresos y gastos."""
    ingresos = calcular_ingresos(mes, anio)
    gastos = calcular_gastos(mes, anio)
    beneficio = ingresos - gastos
    return beneficio

# 4. Obtener importes por categorías en un mes o año
def calcular_importes_por_categoria(mes=None, anio=None):
    """Calcula el importe total de transacciones agrupadas por categoría."""
    filtro = {}
    
    if mes and anio:
        filtro.update({'fecha__month': mes, 'fecha__year': anio})
    elif anio:
        filtro.update({'fecha__year': anio})
    
    importes_por_categoria = (
        Transaccion.objects.filter(**filtro)
        .values('categoria__nombre')
        .annotate(total=Sum('importe'))
        .order_by('-total')
    )
    return importes_por_categoria