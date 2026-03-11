"""
Factory Pattern — Creación de servicios de usuarios y suscripciones.

Centraliza la creación de servicios, permitiendo configurar
dependencias y cambiar implementaciones sin modificar el código cliente.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class UsuarioServiceFactory:
    """
    Factory para crear instancias del servicio de usuarios.

    Uso:
        service = UsuarioServiceFactory.crear()
    """

    @classmethod
    def crear(cls):
        """Crea y retorna una instancia del servicio de usuarios."""
        from usuarios.services.usuario_service import UsuarioService
        logger.info('Factory: Creando UsuarioService')
        return UsuarioService()


class SuscripcionServiceFactory:
    """
    Factory para crear instancias del servicio de suscripciones.

    Uso:
        service = SuscripcionServiceFactory.crear()
    """

    @classmethod
    def crear(cls):
        """Crea y retorna una instancia del servicio de suscripciones."""
        from usuarios.services.suscripcion_service import SuscripcionService
        logger.info('Factory: Creando SuscripcionService')
        return SuscripcionService()



