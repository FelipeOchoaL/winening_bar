"""
Service Layer — Punto de entrada público.

Re-exporta la API pública del paquete de servicios.
Los imports existentes (from pagos.services import ...) siguen funcionando.
"""

from pagos.services.pago_service import PagoService, get_pago_service

__all__ = ['PagoService', 'get_pago_service']

