"""
Modelos de dominio: Usuario y Suscripción.

Usuario extiende AbstractUser de Django para añadir el campo nivelCatador
sin perder la funcionalidad de autenticación integrada.

Suscripción implementa State Pattern para controlar las transiciones
válidas entre estados del ciclo de vida de una suscripción.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Usuario(AbstractUser):
    """
    Usuario del sistema Winening con nivel de catador.

    Extiende AbstractUser para mantener la autenticación de Django
    y añadir atributos de dominio propios.

    Atributos del diagrama:
        - id (heredado de AbstractUser)
        - nombre (first_name + last_name heredados, o username)
        - email (heredado de AbstractUser)
        - nivelCatador → nivel_catador
    """

    class NivelCatador(models.TextChoices):
        PRINCIPIANTE = 'principiante', 'Principiante'
        INTERMEDIO   = 'intermedio',   'Intermedio'
        EXPERTO      = 'experto',      'Experto'

    nivel_catador = models.CharField(
        max_length=20,
        choices=NivelCatador.choices,
        default=NivelCatador.PRINCIPIANTE,
        help_text='Nivel de experiencia del catador',
    )

    # ── Métodos del diagrama ────────────────────────────────────────

    def verificar_acceso_premium(self) -> bool:
        """Verifica si el usuario tiene una suscripción activa."""
        return self.suscripciones.filter(estado=Suscripcion.Estado.ACTIVA).exists()

    def obtener_recomendaciones(self) -> list:
        """
        Obtiene recomendaciones de vinos basadas en el historial
        de catas y nivel del catador.
        """
        # Se puede expandir con lógica de recomendación real
        return []

    def __str__(self) -> str:
        return f'{self.username} ({self.get_nivel_catador_display()})'

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class Suscripcion(models.Model):
    """
    Suscripción de usuario — aplica State Pattern para controlar
    las transiciones válidas entre estados.

    Estados válidos:
        ACTIVA    → CANCELADA
        ACTIVA    → EXPIRADA
        CANCELADA → (estado final)
        EXPIRADA  → ACTIVA  (renovación)

    Relaciones del diagrama:
        - Usuario --tiene--> Suscripción (1 a muchos)
        - Suscripción --genera--> Pago
        - Suscripción --valida estado--> Pago
    """

    # ── Choices ─────────────────────────────────────────────────────
    class Tipo(models.TextChoices):
        MENSUAL  = 'mensual',  'Mensual'
        ANUAL    = 'anual',    'Anual'
        PRUEBA   = 'prueba',   'Prueba Gratuita'

    class Estado(models.TextChoices):
        ACTIVA    = 'activa',    'Activa'
        CANCELADA = 'cancelada', 'Cancelada'
        EXPIRADA  = 'expirada',  'Expirada'

    # ── State Pattern: mapa de transiciones permitidas ──────────────
    TRANSICIONES_VALIDAS: dict[str, list[str]] = {
        Estado.ACTIVA:    [Estado.CANCELADA, Estado.EXPIRADA],
        Estado.CANCELADA: [],                          # estado final
        Estado.EXPIRADA:  [Estado.ACTIVA],             # permite renovación
    }

    # ── Campos ──────────────────────────────────────────────────────
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='suscripciones',
    )
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.MENSUAL,
    )
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVA,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── State Pattern: transición segura ────────────────────────────
    def _transicionar(self, nuevo_estado: str) -> None:
        """Cambia de estado solo si la transición es válida."""
        permitidos = self.TRANSICIONES_VALIDAS.get(self.estado, [])
        if nuevo_estado not in permitidos:
            raise ValidationError(
                f'Transición inválida: {self.estado} → {nuevo_estado}'
            )
        self.estado = nuevo_estado
        self.save(update_fields=['estado', 'updated_at'])

    # ── Métodos del diagrama ────────────────────────────────────────
    def esta_activa(self) -> bool:
        """Verifica si la suscripción está vigente."""
        return (
            self.estado == self.Estado.ACTIVA
            and self.fecha_fin >= timezone.now().date()
        )

    def cancelar(self) -> None:
        """Cancela la suscripción."""
        self._transicionar(self.Estado.CANCELADA)

    def validar_acceso(self) -> bool:
        """
        Valida si la suscripción permite acceso premium.
        Expira automáticamente si la fecha fin ya pasó.
        """
        if self.estado == self.Estado.ACTIVA and self.fecha_fin < timezone.now().date():
            self._transicionar(self.Estado.EXPIRADA)
            return False
        return self.esta_activa()

    # ── Helpers ─────────────────────────────────────────────────────
    def __str__(self) -> str:
        return (
            f'Suscripción {self.get_tipo_display()} — '
            f'{self.usuario.username} ({self.get_estado_display()})'
        )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'



