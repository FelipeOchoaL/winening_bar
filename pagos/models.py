import uuid

from django.db import models
from django.core.exceptions import ValidationError


class Pago(models.Model):
    """
    Modelo Pago — aplica State Pattern para controlar las transiciones
    válidas entre estados del ciclo de vida de un pago.

    Estados válidos:
        PENDIENTE  →  EN_PROCESO  →  COMPLETADO
        PENDIENTE  →  CANCELADO
        EN_PROCESO →  CANCELADO
    """

    # ── Choices (estados) ──────────────────────────────────────────
    class Estado(models.TextChoices):
        PENDIENTE  = 'pendiente',  'Pendiente'
        EN_PROCESO = 'en_proceso', 'En Proceso'
        COMPLETADO = 'completado', 'Completado'
        CANCELADO  = 'cancelado',  'Cancelado'

    class MetodoPago(models.TextChoices):
        TARJETA       = 'tarjeta',       'Tarjeta de Crédito/Débito'
        TRANSFERENCIA = 'transferencia', 'Transferencia Bancaria'
        EFECTIVO      = 'efectivo',      'Efectivo'

    # ── State Pattern: mapa de transiciones permitidas ─────────────
    TRANSICIONES_VALIDAS: dict[str, list[str]] = {
        Estado.PENDIENTE:  [Estado.EN_PROCESO, Estado.CANCELADO],
        Estado.EN_PROCESO: [Estado.COMPLETADO, Estado.CANCELADO],
        Estado.COMPLETADO: [],      # estado final
        Estado.CANCELADO:  [],      # estado final
    }

    # ── Campos ─────────────────────────────────────────────────────
    monto       = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
        default=MetodoPago.TARJETA,
    )
    estado      = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    referencia  = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Identificador único de transacción',
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    # ── State Pattern: transición segura ───────────────────────────
    def _transicionar(self, nuevo_estado: str) -> None:
        """Cambia de estado solo si la transición es válida."""
        permitidos = self.TRANSICIONES_VALIDAS.get(self.estado, [])
        if nuevo_estado not in permitidos:
            raise ValidationError(
                f'Transición inválida: {self.estado} → {nuevo_estado}'
            )
        self.estado = nuevo_estado
        self.save(update_fields=['estado', 'updated_at'])

    # ── Acciones públicas ──────────────────────────────────────────
    def procesar_pago(self) -> dict:
        """
        Mueve el pago a EN_PROCESO y delega al Service Layer.
        Retorna el resultado del procesamiento.
        """
        from pagos.services import get_pago_service     # import diferido
        service = get_pago_service()
        resultado = service.procesar_pago(self)
        return resultado

    def confirmar_pago(self) -> None:
        """Marca el pago como COMPLETADO."""
        self._transicionar(self.Estado.COMPLETADO)

    def cancelar_pago(self) -> None:
        """Marca el pago como CANCELADO."""
        self._transicionar(self.Estado.CANCELADO)

    # ── Helpers ────────────────────────────────────────────────────
    @property
    def esta_completado(self) -> bool:
        return self.estado == self.Estado.COMPLETADO

    def __str__(self) -> str:
        return f'Pago {self.referencia} — ${self.monto} ({self.get_estado_display()})'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
