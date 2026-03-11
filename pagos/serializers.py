"""
Serializers DRF — Transformación Pago ↔ JSON.

Los Serializers se encargan exclusivamente de la serialización
y validación de entrada/salida. NO contienen lógica de negocio.

La lógica de negocio reside en el Service Layer (pagos/services/).
"""

from decimal import Decimal

from rest_framework import serializers

from pagos.models import Pago


class PagoSerializer(serializers.ModelSerializer):
    """
    Serializer de salida para el modelo Pago.
    Transforma una instancia de Pago → JSON.
    """
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True,
    )
    metodo_pago_display = serializers.CharField(
        source='get_metodo_pago_display', read_only=True,
    )

    class Meta:
        model = Pago
        fields = [
            'id',
            'monto',
            'metodo_pago',
            'metodo_pago_display',
            'estado',
            'estado_display',
            'referencia',
            'suscripcion',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'estado', 'estado_display',
            'referencia', 'created_at', 'updated_at',
        ]


class CrearPagoSerializer(serializers.Serializer):
    """
    Serializer de entrada para crear un Pago.

    Solo valida los datos de entrada. La creación real
    se delega al Service Layer (PagoService.crear_pago).
    """
    monto = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.01'),
    )
    metodo_pago = serializers.ChoiceField(
        choices=Pago.MetodoPago.choices,
        default=Pago.MetodoPago.TARJETA,
    )

