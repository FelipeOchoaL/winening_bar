"""
Modelos de dominio: BibliotecaVinos, Vino y NotaSensorial.

BibliotecaVinos es la colección personal de vinos de un usuario.
Vino representa un vino del catálogo del sistema.
NotaSensorial es un Value Object que almacena la evaluación sensorial
de un vino (aroma, color, sabor, textura).
"""

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Vino(models.Model):
    """
    Vino del catálogo del sistema.

    Atributos del diagrama:
        - id (automático)
        - nombre
        - variedad
        - anio (año de cosecha)
        - region
    """

    nombre = models.CharField(max_length=200)
    variedad = models.CharField(
        max_length=100,
        help_text='Variedad de uva (ej: Cabernet Sauvignon, Malbec)',
    )
    anio = models.PositiveIntegerField(
        help_text='Año de cosecha',
    )
    region = models.CharField(
        max_length=100,
        help_text='Región de origen (ej: Mendoza, Valle de Colchagua)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── Métodos del diagrama ────────────────────────────────────────

    def calcular_perfil_sensorial(self) -> dict:
        """
        Calcula el perfil sensorial promedio del vino
        basándose en todas sus notas sensoriales.
        """
        notas = self.notas_sensoriales.all()
        if not notas.exists():
            return {
                'aroma': 0, 'color': 0,
                'sabor': 0, 'textura': 0,
                'total_evaluaciones': 0,
            }

        from django.db.models import Avg
        promedios = notas.aggregate(
            aroma=Avg('aroma'),
            color=Avg('color'),
            sabor=Avg('sabor'),
            textura=Avg('textura'),
        )
        promedios['total_evaluaciones'] = notas.count()
        return promedios

    def es_vino_repetido(self) -> bool:
        """
        Verifica si ya existe otro vino con el mismo nombre,
        variedad y año en el sistema.
        """
        return Vino.objects.filter(
            nombre=self.nombre,
            variedad=self.variedad,
            anio=self.anio,
        ).exclude(pk=self.pk).exists()

    def __str__(self) -> str:
        return f'{self.nombre} ({self.variedad}, {self.anio})'

    class Meta:
        ordering = ['nombre', '-anio']
        verbose_name = 'Vino'
        verbose_name_plural = 'Vinos'


class BibliotecaVinos(models.Model):
    """
    Biblioteca personal de vinos de un usuario.

    Relaciones del diagrama:
        - Usuario --posee--> BibliotecaVinos (1 a 1)
        - BibliotecaVinos --contiene--> Vino (muchos a muchos)
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='biblioteca',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    vinos = models.ManyToManyField(
        Vino,
        related_name='bibliotecas',
        blank=True,
    )

    # ── Métodos del diagrama ────────────────────────────────────────

    def agregar_vino(self, vino: Vino) -> None:
        """Agrega un vino a la biblioteca personal."""
        if vino in self.vinos.all():
            raise ValidationError(
                f'El vino "{vino.nombre}" ya está en la biblioteca.'
            )
        self.vinos.add(vino)

    def remover_vino(self, vino: Vino) -> None:
        """Remueve un vino de la biblioteca personal."""
        if vino not in self.vinos.all():
            raise ValidationError(
                f'El vino "{vino.nombre}" no está en la biblioteca.'
            )
        self.vinos.remove(vino)

    def listar_vinos(self):
        """Retorna todos los vinos de la biblioteca."""
        return self.vinos.all()

    def __str__(self) -> str:
        return f'Biblioteca de {self.usuario.username} ({self.vinos.count()} vinos)'

    class Meta:
        verbose_name = 'Biblioteca de Vinos'
        verbose_name_plural = 'Bibliotecas de Vinos'


class NotaSensorial(models.Model):
    """
    Value Object — Evaluación sensorial de un vino.

    Almacena las puntuaciones de aroma, color, sabor y textura
    en una escala de 1 a 10.

    Relación del diagrama:
        - Cata --registra--> NotaSensorial (composición)
        - NotaSensorial evalúa un Vino
    """

    vino = models.ForeignKey(
        Vino,
        on_delete=models.CASCADE,
        related_name='notas_sensoriales',
    )
    aroma = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Puntuación de aroma (1-10)',
    )
    color = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Puntuación de color (1-10)',
    )
    sabor = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Puntuación de sabor (1-10)',
    )
    textura = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Puntuación de textura (1-10)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # ── Métodos del diagrama ────────────────────────────────────────

    def generar_perfil_sensorial(self) -> dict:
        """Genera un diccionario con el perfil sensorial de esta evaluación."""
        return {
            'aroma': self.aroma,
            'color': self.color,
            'sabor': self.sabor,
            'textura': self.textura,
            'promedio': round(
                (self.aroma + self.color + self.sabor + self.textura) / 4, 2
            ),
        }

    def __str__(self) -> str:
        return (
            f'Nota de {self.vino.nombre}: '
            f'A={self.aroma} C={self.color} S={self.sabor} T={self.textura}'
        )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Nota Sensorial'
        verbose_name_plural = 'Notas Sensoriales'



