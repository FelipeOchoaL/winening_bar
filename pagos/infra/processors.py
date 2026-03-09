"""
Procesadores de Pago — Implementaciones del Strategy Pattern.

Define la interfaz abstracta (ProcesadorPagoBase) y sus implementaciones
concretas (Real y Mock) para procesar pagos.

Cada procesador encapsula la lógica de integración con una pasarela
de pagos diferente, permitiendo intercambiarlos sin modificar el
código cliente.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pagos.models import Pago

logger = logging.getLogger(__name__)


# ── Interfaz abstracta (Contrato) ────────────────────────────────────

class ProcesadorPagoBase(ABC):
    """
    Interfaz abstracta para procesadores de pago.
    Define el contrato que deben cumplir todas las implementaciones.
    """

    @abstractmethod
    def procesar(self, pago: Pago) -> dict:
        """Procesa un pago y retorna el resultado."""
        pass

    @abstractmethod
    def get_nombre(self) -> str:
        """Retorna el nombre del procesador."""
        pass


# ── Implementación REAL ──────────────────────────────────────────────

class ProcesadorPagoReal(ProcesadorPagoBase):
    """
    Procesador de pagos real para producción.
    Integra con pasarelas de pago externas (Stripe, MercadoPago, etc.).
    """

    def procesar(self, pago: Pago) -> dict:
        logger.info(
            '[REAL] Procesando pago %s — $%s via %s',
            pago.referencia, pago.monto, pago.metodo_pago
        )
        # Aquí iría la integración real con la pasarela de pagos
        # Ejemplo: stripe.Charge.create(...) o mercadopago.payments.create(...)
        return {
            'exito': True,
            'mensaje': f'Pago procesado exitosamente (ref: {pago.referencia})',
            'metodo': pago.metodo_pago,
            'procesador': 'REAL',
            'gateway_response': {
                'transaction_id': f'TXN-{pago.referencia}',
                'status': 'approved',
            }
        }

    def get_nombre(self) -> str:
        return 'ProcesadorPagoReal'


# ── Implementación MOCK ──────────────────────────────────────────────

class ProcesadorPagoMock(ProcesadorPagoBase):
    """
    Procesador de pagos simulado para desarrollo y testing.
    No realiza llamadas externas, solo simula el comportamiento.
    """

    def procesar(self, pago: Pago) -> dict:
        logger.info(
            '[MOCK] Simulando procesamiento de pago %s — $%s via %s',
            pago.referencia, pago.monto, pago.metodo_pago
        )
        # Simulación sin llamadas externas
        return {
            'exito': True,
            'mensaje': f'[MOCK] Pago simulado correctamente (ref: {pago.referencia})',
            'metodo': pago.metodo_pago,
            'procesador': 'MOCK',
            'gateway_response': {
                'transaction_id': f'MOCK-TXN-{pago.referencia}',
                'status': 'simulated',
            }
        }

    def get_nombre(self) -> str:
        return 'ProcesadorPagoMock'

