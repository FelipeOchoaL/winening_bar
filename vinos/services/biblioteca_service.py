"""
BibliotecaService — Orquestación de la lógica de negocio de vinos y biblioteca.

El servicio orquesta:
- Builder: Para construir objetos Vino y BibliotecaVinos válidos.
- Operaciones de biblioteca: agregar/remover vinos.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from vinos.domain.builders import VinoBuilder, BibliotecaVinosBuilder

if TYPE_CHECKING:
    from vinos.models import Vino, BibliotecaVinos

logger = logging.getLogger(__name__)


class BibliotecaService:
    """
    Servicio de aplicación para operaciones de vinos y biblioteca.

    Uso:
        service = BibliotecaService()
        vino = service.crear_vino(nombre='Catena', variedad='Malbec', anio=2020, region='Mendoza')
    """

    def crear_vino(
        self,
        nombre: str,
        variedad: str,
        anio: int | str,
        region: str,
    ) -> Vino:
        """
        Crea un nuevo vino usando el Builder.

        Args:
            nombre: Nombre del vino.
            variedad: Variedad de uva.
            anio: Año de cosecha.
            region: Región de origen.

        Returns:
            Vino: Instancia del vino creado.

        Raises:
            ValidationError: Si los datos no son válidos.
        """
        logger.info('Creando vino: %s (%s, %s)', nombre, variedad, anio)

        vino = (
            VinoBuilder()
            .con_nombre(nombre)
            .con_variedad(variedad)
            .con_anio(anio)
            .con_region(region)
            .build()
        )

        logger.info('Vino creado exitosamente: %s', vino)
        return vino

    def obtener_o_crear_biblioteca(self, usuario) -> BibliotecaVinos:
        """
        Obtiene la biblioteca del usuario, o la crea si no existe.

        Args:
            usuario: Usuario dueño de la biblioteca.

        Returns:
            BibliotecaVinos: Biblioteca del usuario.
        """
        from vinos.models import BibliotecaVinos
        biblioteca, created = BibliotecaVinos.objects.get_or_create(
            usuario=usuario,
        )
        if created:
            logger.info('Biblioteca creada para usuario: %s', usuario.username)
        return biblioteca

    def agregar_vino_a_biblioteca(self, usuario, vino: Vino) -> None:
        """Agrega un vino a la biblioteca del usuario."""
        biblioteca = self.obtener_o_crear_biblioteca(usuario)
        biblioteca.agregar_vino(vino)
        logger.info(
            'Vino "%s" agregado a biblioteca de %s',
            vino.nombre, usuario.username,
        )

    def remover_vino_de_biblioteca(self, usuario, vino: Vino) -> None:
        """Remueve un vino de la biblioteca del usuario."""
        biblioteca = self.obtener_o_crear_biblioteca(usuario)
        biblioteca.remover_vino(vino)
        logger.info(
            'Vino "%s" removido de biblioteca de %s',
            vino.nombre, usuario.username,
        )

    def listar_vinos_biblioteca(self, usuario):
        """Lista los vinos de la biblioteca del usuario."""
        biblioteca = self.obtener_o_crear_biblioteca(usuario)
        return biblioteca.listar_vinos()

    def listar_todos_los_vinos(self):
        """Lista todos los vinos del catálogo."""
        from vinos.models import Vino
        return Vino.objects.all()


# ── Factory function ─────────────────────────────────────────────────

def get_biblioteca_service() -> BibliotecaService:
    """
    Factory function para obtener una instancia del servicio.

    Returns:
        BibliotecaService: Instancia del servicio configurada.
    """
    return BibliotecaService()



