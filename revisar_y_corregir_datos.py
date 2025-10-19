import sqlite3
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

def revisar_y_corregir_datos():
    ruta_db_externa = r'CONTABILIDAD.sqlite3'
    conexion = sqlite3.connect(ruta_db_externa)
    cursor = conexion.cursor()

    # Revisar y corregir fechas no válidas
    cursor.execute("SELECT id, fecha FROM contabilidad_transaccion")
    transacciones = cursor.fetchall()
    for transaccion in transacciones:
        id_transaccion, fecha = transaccion
        try:
            # Intentar convertir la fecha al formato correcto
            datetime.strptime(fecha, "%Y-%m-%d")
        except (ValueError, TypeError):
            # Si falla, asignar la fecha actual
            nueva_fecha = date.today().strftime("%Y-%m-%d")
            cursor.execute(
                "UPDATE contabilidad_transaccion SET fecha = ? WHERE id = ?",
                (nueva_fecha, id_transaccion)
            )

    # Revisar y corregir importes no válidos
    cursor.execute("SELECT id, importe FROM contabilidad_transaccion")
    transacciones = cursor.fetchall()
    for transaccion in transacciones:
        id_transaccion, importe = transaccion
        try:
            # Intentar convertir el importe a decimal
            Decimal(importe)
        except (InvalidOperation, ValueError, TypeError):
            # Si falla, asignar un importe predeterminado (por ejemplo, 0.0)
            nuevo_importe = 0.0
            cursor.execute(
                "UPDATE contabilidad_transaccion SET importe = ? WHERE id = ?",
                (nuevo_importe, id_transaccion)
            )

    # Confirmar los cambios
    conexion.commit()
    conexion.close()

    print("Datos revisados y corregidos correctamente.")