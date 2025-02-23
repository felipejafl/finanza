from django.db import models

# Create your models here.
class Cuenta(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=(('activo', 'Activo'), ('pasivo', 'Pasivo'), ('patrimonio neto', 'Patrimonio Neto'), ('ingreso', 'Ingreso'), ('gasto', 'Gasto')))
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre
    
class Transaccion(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255, null=True)
    importe = models.DecimalField(max_digits=10, decimal_places=2)  # Cambiado a DecimalField
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE)

class Presupuesto(models.Model):
    id = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=(('activo', 'Activo'), ('pasivo', 'Pasivo'), ('patrimonio neto', 'Patrimonio Neto'), ('ingreso', 'Ingreso'), ('gasto', 'Gasto')), default='gasto')
    importe = models.DecimalField(max_digits=10, decimal_places=2)

class TicketImagen(models.Model):
    imagen = models.ImageField(upload_to='tickets/')
    cargado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket subido el {self.cargado_en}"
