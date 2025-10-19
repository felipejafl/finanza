from django.db import models
from django.core.serializers import serialize, deserialize
import csv
from io import StringIO

# Create your models here.
class Cuenta(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=(('activo', 'Activo'), ('pasivo', 'Pasivo'), ('patrimonio neto', 'Patrimonio Neto'), ('ingreso', 'Ingreso'), ('gasto', 'Gasto')))
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.nombre

    @staticmethod
    def export_to_csv():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'nombre', 'tipo', 'saldo'])
        for cuenta in Cuenta.objects.all():
            writer.writerow([cuenta.id, cuenta.nombre, cuenta.tipo, cuenta.saldo])
        return output.getvalue()

    @staticmethod
    def import_from_csv(csv_data):
        input_data = StringIO(csv_data)
        reader = csv.DictReader(input_data)
        for row in reader:
            Cuenta.objects.update_or_create(
                id=row['id'],
                defaults={
                    'nombre': row['nombre'],
                    'tipo': row['tipo'],
                    'saldo': row['saldo']
                }
            )

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre

    @staticmethod
    def export_to_csv():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'nombre'])
        for categoria in Categoria.objects.all():
            writer.writerow([categoria.id, categoria.nombre])
        return output.getvalue()

    @staticmethod
    def import_from_csv(csv_data):
        input_data = StringIO(csv_data)
        reader = csv.DictReader(input_data)
        for row in reader:
            Categoria.objects.update_or_create(
                id=row['id'],
                defaults={'nombre': row['nombre']}
            )
    
class Transaccion(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255, null=True)
    importe = models.DecimalField(max_digits=10, decimal_places=2)  # Cambiado a DecimalField
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE)

    @staticmethod
    def export_to_csv():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'fecha', 'descripcion', 'importe', 'categoria_id', 'cuenta_id'])
        for transaccion in Transaccion.objects.all():
            writer.writerow([
                transaccion.id, transaccion.fecha, transaccion.descripcion,
                transaccion.importe, transaccion.categoria_id, transaccion.cuenta_id
            ])
        return output.getvalue()

    @staticmethod
    def import_from_csv(csv_data):
        input_data = StringIO(csv_data)
        reader = csv.DictReader(input_data)
        for row in reader:
            Transaccion.objects.update_or_create(
                id=row['id'],
                defaults={
                    'fecha': row['fecha'],
                    'descripcion': row['descripcion'],
                    'importe': row['importe'],
                    'categoria_id': row['categoria_id'],
                    'cuenta_id': row['cuenta_id']
                }
            )

class Presupuesto(models.Model):
    id = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=(('activo', 'Activo'), ('pasivo', 'Pasivo'), ('patrimonio neto', 'Patrimonio Neto'), ('ingreso', 'Ingreso'), ('gasto', 'Gasto')), default='gasto')
    importe = models.DecimalField(max_digits=10, decimal_places=2)

    @staticmethod
    def export_to_csv():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'categoria_id', 'tipo', 'importe'])
        for presupuesto in Presupuesto.objects.all():
            writer.writerow([presupuesto.id, presupuesto.categoria_id, presupuesto.tipo, presupuesto.importe])
        return output.getvalue()

    @staticmethod
    def import_from_csv(csv_data):
        input_data = StringIO(csv_data)
        reader = csv.DictReader(input_data)
        for row in reader:
            Presupuesto.objects.update_or_create(
                id=row['id'],
                defaults={
                    'categoria_id': row['categoria_id'],
                    'tipo': row['tipo'],
                    'importe': row['importe']
                }
            )

class TicketImagen(models.Model):
    imagen = models.FileField(upload_to='tickets/')
    cargado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket subido el {self.cargado_en}"

    @staticmethod
    def export_to_csv():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'imagen', 'cargado_en'])
        for ticket in TicketImagen.objects.all():
            writer.writerow([ticket.id, ticket.imagen.name, ticket.cargado_en])
        return output.getvalue()

    @staticmethod
    def import_from_csv(csv_data):
        input_data = StringIO(csv_data)
        reader = csv.DictReader(input_data)
        for row in reader:
            TicketImagen.objects.update_or_create(
                id=row['id'],
                defaults={
                    'imagen': row['imagen'],
                    'cargado_en': row['cargado_en']
                }
            )
