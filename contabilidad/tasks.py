# tasks.py
from celery import shared_task
from .models import Transaccion
#from .importarDB import importar_transacciones  # Función de importación
from .importar_datos import importar_datos_desde_sqlite  # Función de importación desde SQLite
@shared_task
def importar_transacciones(archivo):
    # Llama a tu función de importación con el archivo
    importar_transacciones(archivo)
