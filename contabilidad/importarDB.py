from django.forms import ValidationError
import pandas as pd
from .models import Transaccion, Categoria, Cuenta

def importar_transacciones(ruta_archivo):
    # Transaccion.objects.all().delete()
    # # Reiniciar la secuencia
    # from django.db import connection
    # with connection.cursor() as cursor:
    #     cursor.execute("DELETE FROM sqlite_sequence WHERE name='contabilidad_transaccion';")
    print(ruta_archivo)
    df = pd.read_excel(ruta_archivo)

    # Crear las transacciones
    for index, row in df.iterrows():
        try:
            # Obtener la categoría por nombre
            categoria = Categoria.objects.get(nombre=row['categoria'])

            # Obtener la cuenta por nombre
            cuenta = Cuenta.objects.get(nombre=row['cuenta'])
            # Crear el objeto Transaccion
            transaccion = Transaccion(
                fecha=row['fecha'],
                descripcion=row['descripcion'],
                importe=row['importe'],
                categoria=categoria,
                cuenta=cuenta
            )
            transaccion.full_clean()  # Realiza todas las validaciones
            transaccion.save()
        except (Categoria.DoesNotExist, Cuenta.DoesNotExist) as e:
            # Manejar el error si la categoría o cuenta no existe
            print(f"Error al encontrar la categoría o cuenta: {e};"+row['categoria'],row['cuenta'])
        except ValidationError as e:
            # Manejar el error de validación
            print(f"Error al guardar la transacción: {e};"+str(row['importe']))
