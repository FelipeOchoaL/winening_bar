"""
Factory Pattern — Creación de procesadores de pago según el entorno.

ProcesadorPagoFactory decide qué implementación de procesador usar
basándose en la variable de entorno PAYMENT_PROCESSOR_TYPE:
- 'REAL': Usa el procesador real que integra con pasarelas de pago.
- 'MOCK': Usa un procesador simulado para desarrollo y testing.

Esto permite cambiar el comportamiento sin modificar el código,
cumpliendo con el principio Open/Closed de SOLID.
"""

from __future__ import annotations

import logging
import os
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


# ── Factory ──────────────────────────────────────────────────────────

class ProcesadorPagoFactory:
    """
    Factory para crear instancias de procesadores de pago.
    
    Decide qué implementación usar basándose en la variable de entorno
    PAYMENT_PROCESSOR_TYPE:
    - 'REAL': Retorna ProcesadorPagoReal (producción)
    - 'MOCK' o no definida: Retorna ProcesadorPagoMock (desarrollo)
    
    Uso:
        procesador = ProcesadorPagoFactory.crear()
        resultado = procesador.procesar(pago)
    """

    _ENV_VAR_NAME = 'PAYMENT_PROCESSOR_TYPE'

    @classmethod
    def crear(cls) -> ProcesadorPagoBase:
        """
        Crea y retorna la instancia apropiada del procesador de pagos.
        
        Returns:
            ProcesadorPagoBase: Instancia del procesador según el entorno.
        """
        tipo = os.environ.get(cls._ENV_VAR_NAME, 'MOCK').upper()

        if tipo == 'REAL':
            logger.info('Factory: Creando ProcesadorPagoReal (producción)')
            return ProcesadorPagoReal()
        else:
            logger.info('Factory: Creando ProcesadorPagoMock (desarrollo)')
            return ProcesadorPagoMock()

    @classmethod
    def crear_mock(cls) -> ProcesadorPagoMock:
        """Crea explícitamente un procesador mock (útil para tests)."""
        return ProcesadorPagoMock()

    @classmethod
    def crear_real(cls) -> ProcesadorPagoReal:
        """Crea explícitamente un procesador real."""
        return ProcesadorPagoReal()

