"""
UsuarioService — Orquestación de la lógica de negocio de usuarios.

El servicio orquesta:
- Builder: Para construir objetos Usuario válidos.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from usuarios.domain.builders import UsuarioBuilder

if TYPE_CHECKING:
    from usuarios.models import Usuario

logger = logging.getLogger(__name__)


class UsuarioService:
    """
    Servicio de aplicación para operaciones de usuarios.

    Uso:
        service = UsuarioService()
        usuario = service.crear_usuario(
            username='juan',
            email='juan@email.com',
            password='secreto123',
        )
    """

    def crear_usuario(
        self,
        username: str,
        email: str = '',
        first_name: str = '',
        last_name: str = '',
        password: str | None = None,
        nivel_catador: str = 'principiante',
    ) -> Usuario:
        """
        Crea un nuevo usuario usando el Builder.

        Args:
            username: Nombre de usuario (requerido).
            email: Email del usuario.
            first_name: Nombre.
            last_name: Apellido.
            password: Contraseña.
            nivel_catador: Nivel de catador (principiante, intermedio, experto).

        Returns:
            Usuario: Instancia del usuario creado.

        Raises:
            ValidationError: Si los datos no son válidos.
        """
        logger.info('Creando usuario: %s', username)

        builder = (
            UsuarioBuilder()
            .con_username(username)
            .con_email(email)
            .con_nombre(first_name, last_name)
            .con_nivel_catador(nivel_catador)
        )

        if password:
            builder.con_password(password)

        usuario = builder.build()

        logger.info('Usuario creado exitosamente: %s', usuario.username)
        return usuario

    def obtener_usuario(self, pk: int) -> Usuario:
        """Obtiene un usuario por su ID."""
        from usuarios.models import Usuario
        return Usuario.objects.get(pk=pk)

    def listar_usuarios(self):
        """Lista todos los usuarios."""
        from usuarios.models import Usuario
        return Usuario.objects.all()


# ── Factory function ─────────────────────────────────────────────────

def get_usuario_service() -> UsuarioService:
    """
    Factory function para obtener una instancia del servicio.

    Returns:
        UsuarioService: Instancia del servicio configurada.
    """
    return UsuarioService()



