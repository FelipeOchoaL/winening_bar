"""
Builder Pattern — Construcción de objetos Usuario y Suscripción
de forma fluida y validada.

Implementa Fluent Interface para encadenamiento de métodos,
garantizando que los objetos sean válidos antes de persistirlos.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.utils import timezone

if TYPE_CHECKING:
    from usuarios.models import Usuario, Suscripcion


class UsuarioBuilder:
    """
    Builder para construir objetos Usuario de manera fluida y segura.

    Uso:
        usuario = (UsuarioBuilder()
            .con_username('juan')
            .con_email('juan@email.com')
            .con_nombre('Juan', 'Pérez')
            .con_nivel_catador('intermedio')
            .build())
    """

    def __init__(self) -> None:
        self._username: str | None = None
        self._email: str = ''
        self._first_name: str = ''
        self._last_name: str = ''
        self._password: str | None = None
        self._nivel_catador: str = 'principiante'
        self._errors: list[str] = []

    def con_username(self, username: str) -> UsuarioBuilder:
        """Establece el nombre de usuario."""
        if not username or not username.strip():
            self._errors.append('El username es requerido.')
        else:
            self._username = username.strip()
        return self

    def con_email(self, email: str) -> UsuarioBuilder:
        """Establece el email del usuario."""
        self._email = email.strip() if email else ''
        return self

    def con_nombre(self, first_name: str, last_name: str = '') -> UsuarioBuilder:
        """Establece el nombre completo del usuario."""
        self._first_name = first_name.strip() if first_name else ''
        self._last_name = last_name.strip() if last_name else ''
        return self

    def con_password(self, password: str) -> UsuarioBuilder:
        """Establece la contraseña del usuario."""
        if not password or len(password) < 6:
            self._errors.append('La contraseña debe tener al menos 6 caracteres.')
        else:
            self._password = password
        return self

    def con_nivel_catador(self, nivel: str) -> UsuarioBuilder:
        """Establece el nivel de catador."""
        from usuarios.models import Usuario
        niveles_validos = [choice[0] for choice in Usuario.NivelCatador.choices]
        if nivel not in niveles_validos:
            self._errors.append(
                f'Nivel de catador inválido: {nivel}. '
                f'Opciones válidas: {niveles_validos}'
            )
        else:
            self._nivel_catador = nivel
        return self

    def _validar(self) -> None:
        """Valida que el objeto sea construible."""
        if self._username is None:
            self._errors.append('El username es requerido.')

        if self._errors:
            raise ValidationError(self._errors)

    def build(self, save: bool = True) -> Usuario:
        """
        Construye y retorna el objeto Usuario.

        Args:
            save: Si es True, guarda el objeto en la base de datos.

        Returns:
            Instancia de Usuario validada.

        Raises:
            ValidationError: Si el objeto no es válido.
        """
        self._validar()

        from usuarios.models import Usuario
        usuario = Usuario(
            username=self._username,
            email=self._email,
            first_name=self._first_name,
            last_name=self._last_name,
            nivel_catador=self._nivel_catador,
        )

        if self._password:
            usuario.set_password(self._password)

        if save:
            usuario.full_clean()
            usuario.save()

        return usuario


class SuscripcionBuilder:
    """
    Builder para construir objetos Suscripción de manera fluida y segura.

    Uso:
        suscripcion = (SuscripcionBuilder()
            .para_usuario(usuario)
            .con_tipo('anual')
            .con_fechas(inicio, fin)
            .build())
    """

    def __init__(self) -> None:
        self._usuario = None
        self._tipo: str = 'mensual'
        self._fecha_inicio: date | None = None
        self._fecha_fin: date | None = None
        self._errors: list[str] = []

    def para_usuario(self, usuario) -> SuscripcionBuilder:
        """Establece el usuario de la suscripción."""
        if usuario is None:
            self._errors.append('El usuario es requerido.')
        else:
            self._usuario = usuario
        return self

    def con_tipo(self, tipo: str) -> SuscripcionBuilder:
        """Establece el tipo de suscripción."""
        from usuarios.models import Suscripcion
        tipos_validos = [choice[0] for choice in Suscripcion.Tipo.choices]
        if tipo not in tipos_validos:
            self._errors.append(
                f'Tipo de suscripción inválido: {tipo}. '
                f'Opciones válidas: {tipos_validos}'
            )
        else:
            self._tipo = tipo
        return self

    def con_fechas(
        self,
        inicio: date | None = None,
        fin: date | None = None,
    ) -> SuscripcionBuilder:
        """Establece las fechas de inicio y fin."""
        self._fecha_inicio = inicio or timezone.now().date()

        if fin is None:
            # Calcular fecha fin según el tipo
            if self._tipo == 'anual':
                self._fecha_fin = self._fecha_inicio + timedelta(days=365)
            elif self._tipo == 'prueba':
                self._fecha_fin = self._fecha_inicio + timedelta(days=7)
            else:  # mensual
                self._fecha_fin = self._fecha_inicio + timedelta(days=30)
        else:
            self._fecha_fin = fin

        return self

    def _validar(self) -> None:
        """Valida que el objeto sea construible."""
        if self._usuario is None:
            self._errors.append('El usuario es requerido.')

        if self._fecha_inicio and self._fecha_fin:
            if self._fecha_fin <= self._fecha_inicio:
                self._errors.append('La fecha fin debe ser posterior a la fecha inicio.')

        if self._errors:
            raise ValidationError(self._errors)

    def build(self, save: bool = True) -> Suscripcion:
        """
        Construye y retorna el objeto Suscripción.

        Args:
            save: Si es True, guarda el objeto en la base de datos.

        Returns:
            Instancia de Suscripción validada.

        Raises:
            ValidationError: Si el objeto no es válido.
        """
        # Asegurar fechas por defecto
        if self._fecha_inicio is None:
            self.con_fechas()

        self._validar()

        from usuarios.models import Suscripcion
        suscripcion = Suscripcion(
            usuario=self._usuario,
            tipo=self._tipo,
            fecha_inicio=self._fecha_inicio,
            fecha_fin=self._fecha_fin,
        )

        if save:
            suscripcion.full_clean()
            suscripcion.save()

        return suscripcion



