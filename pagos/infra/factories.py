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

from pagos.infra.processors import (
    ProcesadorPagoBase,
    ProcesadorPagoMock,
    ProcesadorPagoReal,
)

logger = logging.getLogger(__name__)


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
