"""
Serializers DRF — Transformación Vino/Biblioteca/NotaSensorial ↔ JSON.

Los Serializers se encargan exclusivamente de la serialización
y validación de entrada/salida. NO contienen lógica de negocio.

La lógica de negocio reside en el Service Layer (vinos/services/).
"""

from rest_framework import serializers

from vinos.models import Vino, BibliotecaVinos, NotaSensorial


class NotaSensorialSerializer(serializers.ModelSerializer):
    """
    Serializer de salida para NotaSensorial.
    """
    perfil = serializers.SerializerMethodField()

    class Meta:
        model = NotaSensorial
        fields = [
            'id',
            'vino',
            'aroma',
            'color',
            'sabor',
            'textura',
            'perfil',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_perfil(self, obj) -> dict:
        return obj.generar_perfil_sensorial()


class VinoSerializer(serializers.ModelSerializer):
    """
    Serializer de salida para el modelo Vino.
    """
    perfil_sensorial = serializers.SerializerMethodField()

    class Meta:
        model = Vino
        fields = [
            'id',
            'nombre',
            'variedad',
            'anio',
            'region',
            'perfil_sensorial',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_perfil_sensorial(self, obj) -> dict:
        return obj.calcular_perfil_sensorial()


class CrearVinoSerializer(serializers.Serializer):
    """
    Serializer de entrada para crear un Vino.

    Solo valida los datos de entrada. La creación real
    se delega al Service Layer (BibliotecaService.crear_vino).
    """
    nombre = serializers.CharField(max_length=200)
    variedad = serializers.CharField(max_length=100)
    anio = serializers.IntegerField(min_value=1900, max_value=2100)
    region = serializers.CharField(max_length=100)


class BibliotecaVinosSerializer(serializers.ModelSerializer):
    """
    Serializer de salida para BibliotecaVinos.
    """
    vinos = VinoSerializer(many=True, read_only=True)
    cantidad_vinos = serializers.SerializerMethodField()

    class Meta:
        model = BibliotecaVinos
        fields = [
            'id',
            'usuario',
            'fecha_creacion',
            'vinos',
            'cantidad_vinos',
        ]
        read_only_fields = ['id', 'fecha_creacion']

    def get_cantidad_vinos(self, obj) -> int:
        return obj.vinos.count()

