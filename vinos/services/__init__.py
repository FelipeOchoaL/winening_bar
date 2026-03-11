"""
Service Layer — Punto de entrada público.

Re-exporta la API pública del paquete de servicios.
"""

from vinos.services.biblioteca_service import BibliotecaService, get_biblioteca_service

__all__ = [
    'BibliotecaService',
    'get_biblioteca_service',
]



