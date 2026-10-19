from rest_framework import serializers
from .models import Solicitud

class SolicitudSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    fecha_creacion = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Solicitud
        fields = ['id', 'titulo', 'descripcion', 'categoria', 'estado', 'fecha_creacion', 'usuario']
        read_only_fields = ['id', 'fecha_creacion', 'usuario']

    def validate_categoria(self, value):
        validas = ['Hardware', 'Software', 'Redes']
        if value not in validas:
            raise serializers.ValidationError(f"Categoría inválida. Debe ser una de: {', '.join(validas)}")
        return value

    def validate_estado(self, value):
        validos = ['Pendiente', 'En Proceso', 'Resuelto']
        if value not in validos:
            raise serializers.ValidationError(f"Estado inválido. Debe ser uno de: {', '.join(validos)}")
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user
        #restriccion si el usuario no es administrador (staff) no puede modificar el estado
        if not user.is_staff and 'estado' in validated_data:
            raise serializers.ValidationError({"estado": "No tienes permisos para modificar el estado de la solicitud."})
        return super().update(instance, validated_data)