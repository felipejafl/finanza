from django.contrib import admin
from .models import Cuenta, Transaccion, Categoria  # Asumiendo que estos son tus modelos

# Register your models here.
admin.site.register(Cuenta)
admin.site.register(Transaccion)
admin.site.register(Categoria)
