"""
Serializers DRF — Transformación Usuario/Suscripción ↔ JSON.

Los Serializers se encargan exclusivamente de la serialización
y validación de entrada/salida. NO contienen lógica de negocio.

La lógica de negocio reside en el Service Layer (usuarios/services/).
"""

from rest_framework import serializers

from usuarios.models import Usuario, Suscripcion


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer de salida para el modelo Usuario.
    """
    nivel_catador_display = serializers.CharField(
        source='get_nivel_catador_display', read_only=True,
    )
    es_premium = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'nivel_catador',
            'nivel_catador_display',
            'es_premium',
            'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']

    def get_es_premium(self, obj) -> bool:
        return obj.verificar_acceso_premium()


class CrearUsuarioSerializer(serializers.Serializer):
    """
    Serializer de entrada para crear un Usuario.

    Solo valida los datos de entrada. La creación real
    se delega al Service Layer (UsuarioService.crear_usuario).
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, default='')
    first_name = serializers.CharField(max_length=150, required=False, default='')
    last_name = serializers.CharField(max_length=150, required=False, default='')
    password = serializers.CharField(
        min_length=6, required=False, write_only=True,
    )
    nivel_catador = serializers.ChoiceField(
        choices=Usuario.NivelCatador.choices,
        default=Usuario.NivelCatador.PRINCIPIANTE,
    )


class SuscripcionSerializer(serializers.ModelSerializer):
    """
    Serializer de salida para el modelo Suscripción.
    """
    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True,
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True,
    )
    esta_vigente = serializers.SerializerMethodField()

    class Meta:
        model = Suscripcion
        fields = [
            'id',
            'usuario',
            'tipo',
            'tipo_display',
            'fecha_inicio',
            'fecha_fin',
            'estado',
            'estado_display',
            'esta_vigente',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'estado', 'fecha_inicio', 'fecha_fin',
            'created_at', 'updated_at',
        ]

    def get_esta_vigente(self, obj) -> bool:
        return obj.esta_activa()


class CrearSuscripcionSerializer(serializers.Serializer):
    """
    Serializer de entrada para crear una Suscripción.

    Solo valida los datos de entrada. La creación real
    se delega al Service Layer (SuscripcionService.crear_suscripcion).
    """
    tipo = serializers.ChoiceField(
        choices=Suscripcion.Tipo.choices,
        default=Suscripcion.Tipo.MENSUAL,
    )

