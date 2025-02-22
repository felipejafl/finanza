from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from .forms import UploadFileForm  # Formulario para subir archivos
from .tasks import importar_transacciones  # Tarea Celery para importar (opcional)
from .models import Cuenta, Transaccion, Categoria, Presupuesto, TicketImagen
from django.db.models import Sum
from datetime import datetime
from datetime import date
from django.db.models.functions import TruncMonth, TruncYear
from django.contrib import messages
from .forms import CuentaForm, PresupuestoForm, CategoriaForm, TransaccionForm, TicketImagenForm
import pytesseract 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Ruta al ejecutable de Tesseract
from PIL import Image

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

# Simulación de ChatGPT para el flujo
# def enviar_a_chatgpt(texto_extraido):
#     # Aquí iría la llamada real a ChatGPT, pero para pruebas devolveremos un mock
#     return [
#         {"nombre": "Producto A", "precio": 12.50},
#         {"nombre": "Producto B", "precio": 8.99},
#         {"nombre": "Producto C", "precio": 5.75},
#     ]

# Importar la librería IA
import os
import google.generativeai as genai
import json

# Configura tu clave API
genai.configure(api_key="API_KEY")  # Reemplaza con tu clave real

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
