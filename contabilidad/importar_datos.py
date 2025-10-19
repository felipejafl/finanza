import sqlite3
from contabilidad.models import Cuenta, Transaccion, Categoria, Presupuesto
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import logging

# Configurar el registro de errores
logging.basicConfig(
    filename='importar_datos.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def importar_datos_desde_sqlite():
    ruta_db_externa = r'D:\Documentos\Desarrollo\Django\CONTABILIDAD.sqlite3'
    # Conectar al archivo SQLite externo
    conexion = sqlite3.connect(ruta_db_externa)
    cursor = conexion.cursor()

    # Importar datos de la tabla 'contabilidad_cuenta'
    cursor.execute("SELECT * FROM contabilidad_cuenta")
    cuentas = cursor.fetchall()
    for cuenta in cuentas:
        Cuenta.objects.update_or_create(
            id=cuenta[0],
            defaults={
                'nombre': cuenta[1],
                'tipo': cuenta[2],
                'saldo': cuenta[3]
            }
        )

    # Importar datos de la tabla 'contabilidad_transaccion'
    cursor.execute("SELECT * FROM contabilidad_transaccion")
    transacciones = cursor.fetchall()
    transacciones_procesadas = 0
    transacciones_omitidas = 0

    for transaccion in transacciones:
        fecha = transaccion[3]
        if not isinstance(fecha, str):
            fecha = str(fecha)  # Convertir a cadena si no lo es

        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()  # Asegurar formato correcto
        except ValueError:
            logging.error(f"Error al convertir la fecha: {fecha}. Se usará la fecha actual.")
            fecha = date.today()  # Usar la fecha actual como predeterminada

        try:
            importe = Decimal(transaccion[2])  # Validar que el importe sea un número decimal
        except (InvalidOperation, ValueError):
            logging.error(f"Error al convertir el importe: {transaccion[2]}. Se omitirá la transacción.")
            transacciones_omitidas += 1
            continue

        # Validar que los campos obligatorios no estén vacíos
        if not transaccion[1] or not transaccion[4] or not transaccion[5]:
            logging.error(f"Transacción con campos obligatorios vacíos: {transaccion}. Se omitirá la transacción.")
            transacciones_omitidas += 1
            continue

        Transaccion.objects.update_or_create(
            id=transaccion[0],
            defaults={
                'descripcion': transaccion[1],
                'importe': importe,  # Usar el importe validado
                'fecha': fecha,  # Usar la fecha convertida o predeterminada
                'cuenta_id': transaccion[4],
                'categoria_id': transaccion[5]
            }
        )
        transacciones_procesadas += 1

    # Cerrar la conexión
    conexion.close()

    # Mostrar resumen
    print(f"Transacciones procesadas: {transacciones_procesadas}")
    print(f"Transacciones omitidas: {transacciones_omitidas}")

    print("Datos importados correctamente.")