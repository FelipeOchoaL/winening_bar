"""
Builder Pattern — Construcción de objetos Vino y BibliotecaVinos
de forma fluida y validada.

Implementa Fluent Interface para encadenamiento de métodos,
garantizando que los objetos sean válidos antes de persistirlos.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from vinos.models import Vino, BibliotecaVinos


class VinoBuilder:
    """
    Builder para construir objetos Vino de manera fluida y segura.

    Uso:
        vino = (VinoBuilder()
            .con_nombre('Catena Zapata')
            .con_variedad('Malbec')
            .con_anio(2020)
            .con_region('Mendoza')
            .build())
    """

    def __init__(self) -> None:
        self._nombre: str | None = None
        self._variedad: str | None = None
        self._anio: int | None = None
        self._region: str | None = None
        self._errors: list[str] = []

    def con_nombre(self, nombre: str) -> VinoBuilder:
        """Establece el nombre del vino."""
        if not nombre or not nombre.strip():
            self._errors.append('El nombre del vino es requerido.')
        else:
            self._nombre = nombre.strip()
        return self

    def con_variedad(self, variedad: str) -> VinoBuilder:
        """Establece la variedad de uva."""
        if not variedad or not variedad.strip():
            self._errors.append('La variedad es requerida.')
        else:
            self._variedad = variedad.strip()
        return self

    def con_anio(self, anio: int | str) -> VinoBuilder:
        """Establece el año de cosecha."""
        try:
            anio_int = int(anio)
            if anio_int < 1900 or anio_int > 2100:
                self._errors.append(f'Año inválido: {anio}. Debe estar entre 1900 y 2100.')
            else:
                self._anio = anio_int
        except (ValueError, TypeError):
            self._errors.append(f'Año inválido: {anio}')
        return self

    def con_region(self, region: str) -> VinoBuilder:
        """Establece la región de origen."""
        if not region or not region.strip():
            self._errors.append('La región es requerida.')
        else:
            self._region = region.strip()
        return self

    def _validar(self) -> None:
        """Valida que el objeto sea construible."""
        if self._nombre is None:
            self._errors.append('El nombre del vino es requerido.')
        if self._variedad is None:
            self._errors.append('La variedad es requerida.')
        if self._anio is None:
            self._errors.append('El año es requerido.')
        if self._region is None:
            self._errors.append('La región es requerida.')

        if self._errors:
            raise ValidationError(self._errors)

    def build(self, save: bool = True) -> Vino:
        """
        Construye y retorna el objeto Vino.

        Args:
            save: Si es True, guarda el objeto en la base de datos.

        Returns:
            Instancia de Vino validada.

        Raises:
            ValidationError: Si el objeto no es válido.
        """
        self._validar()

        from vinos.models import Vino
        vino = Vino(
            nombre=self._nombre,
            variedad=self._variedad,
            anio=self._anio,
            region=self._region,
        )

        if save:
            vino.full_clean()
            vino.save()

        return vino


class BibliotecaVinosBuilder:
    """
    Builder para construir objetos BibliotecaVinos de manera fluida y segura.

    Uso:
        biblioteca = (BibliotecaVinosBuilder()
            .para_usuario(usuario)
            .build())
    """

    def __init__(self) -> None:
        self._usuario = None
        self._errors: list[str] = []

    def para_usuario(self, usuario) -> BibliotecaVinosBuilder:
        """Establece el usuario dueño de la biblioteca."""
        if usuario is None:
            self._errors.append('El usuario es requerido.')
        else:
            self._usuario = usuario
        return self

    def _validar(self) -> None:
        """Valida que el objeto sea construible."""
        if self._usuario is None:
            self._errors.append('El usuario es requerido.')

        # Verificar que el usuario no tenga ya una biblioteca
        if self._usuario:
            from vinos.models import BibliotecaVinos
            if BibliotecaVinos.objects.filter(usuario=self._usuario).exists():
                self._errors.append(
                    f'El usuario {self._usuario.username} ya tiene una biblioteca.'
                )

        if self._errors:
            raise ValidationError(self._errors)

    def build(self, save: bool = True) -> BibliotecaVinos:
        """
        Construye y retorna el objeto BibliotecaVinos.

        Args:
            save: Si es True, guarda el objeto en la base de datos.

        Returns:
            Instancia de BibliotecaVinos validada.

        Raises:
            ValidationError: Si el objeto no es válido.
        """
        self._validar()

        from vinos.models import BibliotecaVinos
        biblioteca = BibliotecaVinos(
            usuario=self._usuario,
        )

        if save:
            biblioteca.full_clean()
            biblioteca.save()

        return biblioteca



