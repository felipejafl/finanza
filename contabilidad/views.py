from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.db.models import Sum, F, Count
from datetime import datetime, date
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TransaccionSerializer
# Importar los modelos y formularios
from .models import Cuenta, Transaccion, Categoria, Presupuesto
from .forms import CuentaForm, PresupuestoForm, CategoriaForm, TransaccionForm, TicketImagenForm
# Importar la librería IA de Google
import os
import google.generativeai as genai
import json

#Dashboard de inicio
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
    datojs = {}
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(datojs)
    else:
        return render(request, 'contabilidad/index.html', context)
# Cuentas
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

# Transacciones
class TransaccionListAPIView(APIView):
    def get(self, request, *args, **kwargs):
         # Obtener la fecha actual
        hoy = datetime.now()
        # Obtener el primer día del mes actual
        inicio_mes = datetime(hoy.year, hoy.month, 1)
        # Calcular el último día del mes actual
        if hoy.month == 12:
            fin_mes = datetime(hoy.year + 1, 1, 1)
        else:
            fin_mes = datetime(hoy.year, hoy.month + 1, 1)
        
        # Filtrar transacciones dentro del mes actual
        transacciones = Transaccion.objects.filter(
            fecha__gte=inicio_mes,
            fecha__lt=fin_mes
        ).select_related('categoria', 'cuenta')

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

# Configura tu clave API
api_key = os.environ.get("GEMINI_API_KEY") # toma el api de una variable de entorno que se ha creado previamente con la clave
genai.configure(api_key=api_key)  # Reemplaza con tu clave real

def enviar_a_IA(imagen_path):
    """
    Envía una imagen de un comprobante de compra a Gemini y extrae los productos y precios en formato JSON.

    Args:
        imagen_path (str): La ruta al archivo de imagen del comprobante.

    Returns:
        str: La respuesta de Gemini en formato JSON o None si hay un error.
    """
    try:
        # Subir la imagen a Gemini
        file = genai.upload_file(imagen_path, mime_type="image/jpeg")  # Asume que es JPEG, ajusta si es necesario

        # Configuración del modelo
        generation_config = {
            "temperature": 0.3,  # Ajusta la temperatura para controlar la creatividad
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # Crear el mensaje para Gemini
        prompt = f"""
        A partir de la imagen adjunta de un ticket de compra, devuélveme una lista de productos con el nombre del producto y el precio correspondiente. 
        El formato de la respuesta debe ser estrictamente JSON, con este esquema:
        [
            {{"nombre": "Producto A", "precio": 10.50}},
            {{"nombre": "Producto B", "precio": 20.00}}
        ]
        """

        # Iniciar la conversación con Gemini
        #chat_session = model.start_chat(history=[{"role": "user", "parts": [file, prompt]}])

        # Obtener la respuesta de Gemini
        response = model.generate_content([file, prompt], generation_config={'response_mime_type':'application/json'})  # No necesitas pasar un mensaje adicional

        # Devolver la respuesta
        return json.loads(response.text)

    except Exception as e:
        print(f"Error al enviar la imagen a Gemini: {e}")
        return None

def cargar_ticket(request):
    if request.method == 'POST':
        form = TicketImagenForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save()
            # Extraer productos y precios de la imagen del ticket
            productos = enviar_a_IA(ticket.imagen.path)
            # Eliminar la imagen después de procesarla
            if os.path.exists(ticket.imagen.path):
                os.remove(ticket.imagen.path)
            # Obtener cuentas y categorías para los selects
            cuentas = Cuenta.objects.all()
            categorias = Categoria.objects.all()
            return render(request, 'contabilidad/transacciones/resultado.html', {
                'productos': productos,
                'cuentas': cuentas,
                'categorias': categorias,
                'date': date.today().strftime('%Y-%m-%d')
            })
    else:
        form = TicketImagenForm()
    return render(request, 'contabilidad/transacciones/cargar_ticket.html', {'form': form})

def guardar_transacciones(request):
    if request.method == 'POST':
        # Procesar las filas dinámicas
        for key, value in request.POST.items():
            if key.startswith('descripcion_'):
                index = key.split('_')[1]
                descripcion = value
                importe = request.POST.get(f'importe_{index}')
                fecha = request.POST.get(f'fecha_{index}')
                cuenta_id = request.POST.get(f'cuenta_{index}')
                categoria_id = request.POST.get(f'categoria_{index}')
                
                # Crear la transacción
                Transaccion.objects.create(
                    descripcion=descripcion,
                    importe=importe,
                    fecha=datetime.strptime(fecha, '%Y-%m-%d'),
                    cuenta_id=cuenta_id,
                    categoria_id=categoria_id
                )
        return redirect('transaccion_listar')

# Categorías
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

# Presupuestos
def presupuesto_listar(request):
    # Obtener todos los presupuestos
    presupuestos = Presupuesto.objects.all()

# Calcular el total de ingresos
    total_ingresos = presupuestos.filter(tipo='ingreso').aggregate(Sum('importe'))['importe__sum']
    total_ingresos = total_ingresos if total_ingresos else 0  # Evitar None

    # Calcular el total de gastos
    total_gastos = presupuestos.filter(tipo='gasto').aggregate(Sum('importe'))['importe__sum']
    total_gastos = total_gastos if total_gastos else 0  # Evitar None

    # Calcular el total final (ingresos - gastos)
    total = total_ingresos - total_gastos

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

#Reportes

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

# 5. Reporte financiero mensual
from django.db.models.functions import TruncMonth
import locale  # Importamos la biblioteca locale

def reporte_financiero(request):
    """
    Vista para generar el reporte financiero mensual de ingresos vs gastos, con meses en español.
    """
    # Establecer la configuración regional a español (España) - Asegúrate de tener el locale instalado en tu sistema
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') # Intenta con es_ES.UTF-8
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES') # Si UTF-8 falla, intenta con es_ES sin encoding
        except locale.Error:
            locale.setlocale(locale.LC_TIME, '') # Si falla es_ES, usa la configuración regional por defecto del sistema

    transacciones_ingresos = Transaccion.objects.filter(cuenta__tipo='ingreso')
    transacciones_gastos = Transaccion.objects.filter(cuenta__tipo='gasto')

    ingresos_mensuales = transacciones_ingresos.annotate(mes=TruncMonth('fecha')).values('mes').annotate(
        total_ingresos=Sum('importe')
    ).order_by('mes')

    gastos_mensuales = transacciones_gastos.annotate(mes=TruncMonth('fecha')).values('mes').annotate(
        total_gastos=Sum('importe')
    ).order_by('mes')

    reporte_data_list = []
    for ingreso_mes in ingresos_mensuales:
        mes_anio = ingreso_mes['mes']
        gasto_mes_data = next((gasto for gasto in gastos_mensuales if gasto['mes'] == mes_anio), {'total_gastos': 0})
        total_ingresos = ingreso_mes['total_ingresos']
        total_gastos = gasto_mes_data.get('total_gastos', 0)
        beneficio_perdida = total_ingresos - total_gastos

        reporte_data_list.append({
            'mes': mes_anio.strftime('%B'), # strftime formatea usando la configuración regional establecida
            'anio': mes_anio.year,
            'total_ingresos': float(total_ingresos),
            'total_gastos': float(total_gastos),
            'beneficio_perdida': float(beneficio_perdida),
        })

    reporte_data_json = json.dumps(reporte_data_list)

    context = {
        'reporte_data_json': reporte_data_json,
        'reporte_data_list': reporte_data_list,
    }
    return render(request, 'contabilidad/reportes/reporte_financiero.html', context)

# 6. Reporte de gastos por categoría
from django.template.defaultfilters import floatformat # Importa floatformat desde views para usarlo en Python

from django.utils import timezone

def reporte_gastos_por_categoria(request):
    """
    Genera un reporte de gastos por categoría, opcionalmente filtrado por rango de fechas.
    """
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    fecha_inicio = None
    fecha_fin = None

    if fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            transacciones_gasto = Transaccion.objects.filter(
                cuenta__tipo='gasto',
                fecha__range=[fecha_inicio, fecha_fin]
            )
        except ValueError:
            # Si las fechas no son válidas, mostrar reporte del mes actual
            fecha_inicio = timezone.now().date().replace(day=1)
            fecha_fin = timezone.now().date()
            transacciones_gasto = Transaccion.objects.filter(
                cuenta__tipo='gasto',
                fecha__month=fecha_fin.month,
                fecha__year=fecha_fin.year
            )
            fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d') # Formato para el input date
            fecha_fin_str = fecha_fin.strftime('%Y-%m-%d') # Formato para el input date
    else:
        # Por defecto, reporte del mes actual
        fecha_inicio = timezone.now().date().replace(day=1)
        fecha_fin = timezone.now().date()
        transacciones_gasto = Transaccion.objects.filter(
            cuenta__tipo='gasto',
            fecha__month=fecha_fin.month,
            fecha__year=fecha_fin.year
        )
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d') # Formato para el input date
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d') # Formato para el input date


    gastos_por_categoria = transacciones_gasto.values('categoria__nombre').annotate(
        importe_total_gastado=Sum('importe')
    ).order_by('-importe_total_gastado')

    categorias_gastos_data = []
    total_gastos = 0

    for categoria in gastos_por_categoria:
        importe_total = categoria['importe_total_gastado']
        total_gastos += importe_total
        categorias_gastos_data.append({
            'categoria_nombre': categoria['categoria__nombre'],
            'importe_total_gastado': importe_total,
            'porcentaje_gasto': 0
        })

    if total_gastos > 0:
        for categoria_data in categorias_gastos_data:
            porcentaje = (categoria_data['importe_total_gastado'] / total_gastos) * 100
            categoria_data['porcentaje_gasto'] = floatformat(porcentaje, 1)

    context = {
        'categorias_gastos': categorias_gastos_data,
        'total_gastos': total_gastos,
        'fecha_inicio_str': fecha_inicio_str,
        'fecha_fin_str': fecha_fin_str,
    }

    return render(request, 'contabilidad/reportes/reporte_gastos_categoria.html', context)

# 7. Reporte de saldo de cuentas dinámico
def reporte_saldo_cuentas_dinamico(request):
    """
    Genera un reporte de saldo de cuentas dinámico, calculando el saldo actual
    basado en el saldo inicial de la cuenta y las transacciones asociadas.
    Incluye el saldo total general calculado en el backend.
    """
    cuentas = Cuenta.objects.all() # Paso 1: Acceder a todos los registros de Cuenta
    reporte_cuentas = []
    total_saldo = 0 # Inicializar el saldo total general aquí

    for cuenta in cuentas: # Paso 2: Iterar sobre cada cuenta
        saldo_actual_dinamico = cuenta.saldo  # **Inicializar con el saldo inicial de la cuenta**
        transacciones = Transaccion.objects.filter(cuenta=cuenta) # Recuperar transacciones asociadas

        for transaccion in transacciones: # Iterar sobre las transacciones
            tipo_cuenta_transaccion = transaccion.cuenta.tipo # Obtener el tipo de cuenta de la transacción

            if tipo_cuenta_transaccion == 'ingreso': # Si es 'ingreso', sumar al saldo
                saldo_actual_dinamico += transaccion.importe
            elif tipo_cuenta_transaccion == 'gasto': # Si es 'gasto', restar del saldo
                saldo_actual_dinamico -= transaccion.importe
            # Considerar otros tipos de cuenta aquí si es necesario

        # Paso 3: Preparar los datos para la visualización
        reporte_cuentas.append({
            'nombre_cuenta': cuenta.nombre,
            'saldo_actual_dinamico': saldo_actual_dinamico,
            'tipo_cuenta': cuenta.tipo # Opcional, pero útil
        })
        total_saldo += saldo_actual_dinamico # Acumular al saldo total general

    # Paso 4: Ordenar la lista de cuentas alfabéticamente
    reporte_cuentas_ordenado = sorted(reporte_cuentas, key=lambda cuenta: cuenta['nombre_cuenta'])

    context = {
        'reporte_cuentas': reporte_cuentas_ordenado,
        'total_saldo': total_saldo # Pasar el saldo total general al contexto
    }

    return render(request, 'contabilidad/reportes/reporte_saldo_cuentas_dinamico.html', context)

# 8. Reporte de presupuesto mensual vs gastos reales
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
        'meses': range(1, 13),  # Lista de meses (1-12)
        'años': range(hoy.year - 5, hoy.year + 1),  # Últimos 5 años
    }
    return render(request, 'contabilidad/reportes/presupuesto_mensual.html', context)

# 9. Reporte de transacciones filtrado
from .forms import TransaccionFilterForm
from django.db.models import Q

def reporte_transacciones_filtrado(request):
    form = TransaccionFilterForm(request.GET) # Usamos request.GET para formularios de filtro

    transacciones = Transaccion.objects.all().order_by('-fecha') # Transacciones por defecto, ordenadas por fecha descendente
    if form.is_valid():
        fecha_inicio = form.cleaned_data.get('fecha_inicio')
        fecha_fin = form.cleaned_data.get('fecha_fin')
        categorias = form.cleaned_data.get('categorias')
        cuentas = form.cleaned_data.get('cuentas')
        tipo_cuenta = form.cleaned_data.get('tipo_cuenta')
        descripcion_palabra_clave = form.cleaned_data.get('descripcion_palabra_clave')

        # Construcción dinámica de la consulta ORM utilizando Q objects
        query = Q()

        if fecha_inicio:
            query &= Q(fecha__gte=fecha_inicio) # Filtrar por fecha inicio (mayor o igual)
        if fecha_fin:
            query &= Q(fecha__lte=fecha_fin) # Filtrar por fecha fin (menor o igual)
        if categorias:
            query &= Q(categoria__in=categorias) # Filtrar por categorias seleccionadas
        if cuentas:
            query &= Q(cuenta__in=cuentas) # Filtrar por cuentas seleccionadas
        if tipo_cuenta:
            query &= Q(cuenta__tipo=tipo_cuenta) # Filtrar por tipo de cuenta
        if descripcion_palabra_clave:
            query &= Q(descripcion__icontains=descripcion_palabra_clave) # Filtrar descripción por palabra clave (icontains: insensitive case)

        transacciones = Transaccion.objects.filter(query).order_by('-fecha') # Aplicar filtros a las transacciones

    context = {
        'form': form,
        'transacciones': transacciones
    }
    return render(request, 'contabilidad/reportes/reporte_transacciones_filtrado.html', context)

# 10. Reporte de resumen de ingresos por tipo (categoría)

def resumen_ingresos_por_tipo(request):
    """
    Vista de Django para generar un reporte de resumen de ingresos por tipo (categoría).
    Permite seleccionar un rango de fechas para el reporte.
    Si no se especifica un rango, muestra el mes actual por defecto.
    """
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    fecha_inicio = None
    fecha_fin = None

    if fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            transacciones_ingreso = Transaccion.objects.filter(
                cuenta__tipo='ingreso',
                fecha__range=[fecha_inicio, fecha_fin]
            )
            periodo_reporte = f"Desde {fecha_inicio.strftime('%d/%m/%Y')} hasta {fecha_fin.strftime('%d/%m/%Y')}" # Para el título
        except ValueError:
            return HttpResponse("Error: Formato de fecha inválido. Use AAAA-MM-DD.", status=400) # Manejo de error de formato de fecha
    else:
        today = date.today()
        mes_actual = today.month
        anio_actual = today.year
        fecha_inicio = date(anio_actual, mes_actual, 1) # Primer día del mes actual
        fecha_fin = date(anio_actual, mes_actual, today.day) # Día actual del mes actual
        transacciones_ingreso = Transaccion.objects.filter(
            cuenta__tipo='ingreso',
            fecha__month=mes_actual,
            fecha__year=anio_actual
        )
        periodo_reporte = f"Mes Actual ({fecha_inicio.strftime('%B %Y')})" # Para el título

    # 2. Agrupar por categoría y calcular el importe total de ingresos
    ingresos_por_categoria = transacciones_ingreso.values('categoria__nombre').annotate(
        importe_total_ingresos=Sum('importe')
    ).order_by('-importe_total_ingresos')

    # 3. Calcular el total de ingresos para todas las categorías
    total_ingresos = transacciones_ingreso.aggregate(total_ingresos=Sum('importe'))['total_ingresos'] or 0

    # 4. Preparar datos para la plantilla: lista de diccionarios con porcentajes
    categorias_ingresos_data = []
    for categoria_ingreso in ingresos_por_categoria:
        nombre_categoria = categoria_ingreso['categoria__nombre']
        importe_total_ingresos = categoria_ingreso['importe_total_ingresos']
        porcentaje_ingresos_totales = (importe_total_ingresos / total_ingresos) * 100 if total_ingresos else 0
        categorias_ingresos_data.append({
            'nombre_categoria': nombre_categoria,
            'importe_total_ingresos': importe_total_ingresos,
            'porcentaje_ingresos_totales': f'{porcentaje_ingresos_totales:.2f}%', # Formatear porcentaje
        })

    context = {
        'categorias_ingresos_data': categorias_ingresos_data,
        'total_ingresos': total_ingresos,
        'periodo_reporte': periodo_reporte, # Pasar el periodo para el título
    }
    return render(request, 'contabilidad/reportes/resumen_ingresos_por_tipo.html', context)

# 11. Reporte de gastos deducibles
def reporte_gastos_deducibles(request):
    # 1. Definir categorías deducibles (adaptar a la normativa española)
    categorias_deducibles = ["Gastos de Oficina", "Formación", "Viajes", "Asesoría Fiscal", "Seguros Profesionales"]

    # 2. Obtener año fiscal actual (para filtro de tiempo)
    # (TODO: permitir selección de período)
    anio_actual = datetime.now().year  # Import datetime

    # 3. Acceder y filtrar transacciones
    transacciones = Transaccion.objects.filter(
        cuenta__tipo='gasto',  # Cuentas de tipo 'gasto'
        categoria__nombre__in=categorias_deducibles,  # Categorías deducibles
        fecha__year=anio_actual  # Año fiscal actual (TODO: permitir rango de fechas)
    ).annotate(nombre_categoria=F('categoria__nombre'))  # Añadir nombre_categoria

    # 4. Agrupar y calcular totales por categoría
    gastos_por_categoria = transacciones.values('nombre_categoria').annotate(
        importe_total_deducible=Sum('importe')
    ).order_by('-importe_total_deducible')

    # 5. Calcular porcentaje de gastos deducibles totales
    total_gastos_deducibles = gastos_por_categoria.aggregate(Sum('importe_total_deducible'))['importe_total_deducible__sum'] or 0

    for categoria in gastos_por_categoria:
        categoria['porcentaje_deducible_total_gastos'] = (
            (categoria['importe_total_deducible'] / total_gastos_deducibles) * 100 if total_gastos_deducibles else 0
        )

    # 6. Preparar datos para la plantilla
    context = {
        'gastos_por_categoria': gastos_por_categoria,
        'total_gastos_deducibles': total_gastos_deducibles,
    }

    return render(request, 'contabilidad/reportes/reporte_gastos_deducibles.html', context)

from decimal import Decimal

# 12. Reporte de IVA
def reporte_iva(request):
    # 1. Definir el período del reporte (TRIMESTRE ACTUAL por defecto)
    # **NOTA IMPORTANTE**: La lógica para el filtro de tiempo se implementará en el futuro
    # Para este ejemplo, usaremos el trimestre actual.
    import datetime
    today = datetime.date.today()
    current_quarter = (today.month - 1) // 3 + 1
    start_month = (current_quarter - 1) * 3 + 1
    end_month = current_quarter * 3
    start_date = datetime.date(today.year, start_month, 1)
    end_date = datetime.date(today.year, end_month, 1)

    # 2. Identificar transacciones (CRITERIO SIMPLIFICADO: tipo de cuenta)
    transacciones_gastos = Transaccion.objects.filter(cuenta__tipo='gasto', fecha__range=(start_date, end_date))
    transacciones_ingresos = Transaccion.objects.filter(cuenta__tipo='ingreso', fecha__range=(start_date, end_date))

    # 3. Calcular IVA Soportado
    total_iva_soportado = 0
    for transaccion in transacciones_gastos:
        base_imponible = transaccion.importe / Decimal('1.21')  # Convertir a Decimal
        iva_soportado = transaccion.importe - base_imponible
        total_iva_soportado += iva_soportado

    # 4. Calcular IVA Repercutido
    total_iva_repercutido = 0
    for transaccion in transacciones_ingresos:
        base_imponible = transaccion.importe / Decimal('1.21')  # Convertir a Decimal
        iva_repercutido = transaccion.importe - base_imponible
        total_iva_repercutido += iva_repercutido

    # 5. Preparar datos para la plantilla
    context = {
        'periodo_reporte': f"Trimestre {current_quarter} {today.year}", # Ejemplo: Trimestre 3 2024
        'total_iva_soportado': total_iva_soportado,
        'total_iva_repercutido': total_iva_repercutido,
        'diferencia_iva': total_iva_repercutido - total_iva_soportado,
    }

    return render(request, 'contabilidad/reportes/reporte_iva.html', context)

# 13. Reporte de Retenciones de IRPF
def obtener_periodo_trimestre_actual():
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    if 1 <= mes_actual <= 3:
        inicio_trimestre = date(anio_actual, 1, 1)
        fin_trimestre = date(anio_actual, 3, 31)
        periodo_reporte = f"1er Trimestre {anio_actual}"
    elif 4 <= mes_actual <= 6:
        inicio_trimestre = date(anio_actual, 4, 1)
        fin_trimestre = date(anio_actual, 6, 30)
        periodo_reporte = f"2º Trimestre {anio_actual}"
    elif 7 <= mes_actual <= 9:
        inicio_trimestre = date(anio_actual, 7, 1)
        fin_trimestre = date(anio_actual, 9, 30)
        periodo_reporte = f"3er Trimestre {anio_actual}"
    else: # 10 <= mes_actual <= 12
        inicio_trimestre = date(anio_actual, 10, 1)
        fin_trimestre = date(anio_actual, 12, 31)
        periodo_reporte = f"4º Trimestre {anio_actual}"

    return inicio_trimestre, fin_trimestre, periodo_reporte

def reporte_retenciones_irpf(request):
    """
    Vista de Django para generar un reporte de Retenciones de IRPF de facturas.
    """
    inicio_trimestre, fin_trimestre, periodo_reporte = obtener_periodo_trimestre_actual()

    # 1. Definir categorías que generan retención de IRPF (ADAPTAR A TUS CATEGORÍAS REALES)
    categorias_con_retencion = ["Servicios Profesionales", "Alquileres"]

    # 2. Acceder y filtrar transacciones
    transacciones = Transaccion.objects.filter(
        fecha__range=(inicio_trimestre, fin_trimestre), # Filtrar por período
        categoria__in=categorias_con_retencion # Filtrar por categoría
    )

    reporte_data = []
    total_base_imponible_periodo = 0
    total_importe_retenido_periodo = 0
    porcentaje_retencion = 15 # Porcentaje de retención general (ADAPTAR SI ES NECESARIO)
    tipo_iva = 0.21 # Tipo de IVA general 21%

    for transaccion in transacciones:
        # 3. Calcular Base Imponible (asumiendo IVA incluido)
        base_imponible = transaccion.importe / (1 + tipo_iva)

        # 4. Calcular Importe Retenido
        importe_retenido = base_imponible * (porcentaje_retencion / 100)

        reporte_data.append({
            'fecha': transaccion.fecha,
            'categoria': transaccion.categoria,
            'importe_total': transaccion.importe,
            'base_imponible': base_imponible,
            'porcentaje_retencion': porcentaje_retencion,
            'importe_retenido': importe_retenido,
        })

        total_base_imponible_periodo += base_imponible
        total_importe_retenido_periodo += importe_retenido

    context = {
        'periodo_reporte': periodo_reporte,
        'reporte_data': reporte_data,
        'total_base_imponible_periodo': total_base_imponible_periodo,
        'total_importe_retenido_periodo': total_importe_retenido_periodo,
        'porcentaje_retencion_aplicado': porcentaje_retencion, # Pasar el porcentaje a la plantilla
    }

   
    return render(request, 'contabilidad/reportes/reporte_retenciones_irpf.html', context)
