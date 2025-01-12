# tasks.py
from celery import shared_task
from .models import Transaccion
from .importarDB import importar_transacciones  # Función de importación

@shared_task
def importar_transacciones(archivo):
    # Llama a tu función de importación con el archivo
    importar_transacciones(archivo)
