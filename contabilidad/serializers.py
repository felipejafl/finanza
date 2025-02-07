from rest_framework import serializers
from .models import Transaccion

class TransaccionSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    cuenta_nombre = serializers.CharField(source='cuenta.nombre', read_only=True)
    fecha = serializers.DateField(format=None)
    class Meta:
        model = Transaccion
        fields = ['id', 'fecha', 'descripcion', 'importe', 'categoria_nombre', 'cuenta_nombre']
