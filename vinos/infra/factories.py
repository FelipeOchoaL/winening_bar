"""
Factory Pattern — Creación de servicios de vinos y biblioteca.

Centraliza la creación de servicios, permitiendo configurar
dependencias y cambiar implementaciones sin modificar el código cliente.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class BibliotecaServiceFactory:
    """
    Factory para crear instancias del servicio de biblioteca de vinos.

    Uso:
        service = BibliotecaServiceFactory.crear()
    """

    @classmethod
    def crear(cls):
        """Crea y retorna una instancia del servicio de biblioteca."""
        from vinos.services.biblioteca_service import BibliotecaService
        logger.info('Factory: Creando BibliotecaService')
        return BibliotecaService()



