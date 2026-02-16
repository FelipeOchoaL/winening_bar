"""
Service Layer — Orquestación de la lógica de negocio de pagos.

PagoService es el punto de entrada para todas las operaciones de pago.
Implementa Inyección de Dependencias: recibe el procesador de pagos
como dependencia, lo que permite cambiar la implementación fácilmente
(útil para testing y diferentes entornos).

El servicio orquesta:
- Builder: Para construir objetos Pago válidos.
- Factory: Para obtener el procesador de pagos adecuado.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pagos.domain.builders import PagoBuilder
from pagos.infra.factories import ProcesadorPagoBase, ProcesadorPagoFactory

if TYPE_CHECKING:
    from decimal import Decimal
    from pagos.models import Pago

logger = logging.getLogger(__name__)


class PagoService:
    """
    Servicio de aplicación para operaciones de pago.
    
    Implementa Inyección de Dependencias: el procesador de pagos
    se inyecta en el constructor, permitiendo usar diferentes
    implementaciones (MOCK para desarrollo, REAL para producción).
    
    Uso:
        # Con Factory (recomendado)
        service = PagoService()
        
        # Con inyección explícita (útil para tests)
        mock_procesador = ProcesadorPagoFactory.crear_mock()
        service = PagoService(procesador=mock_procesador)
    """

    def __init__(self, procesador: ProcesadorPagoBase | None = None) -> None:
        """
        Inicializa el servicio con un procesador de pagos.
        
        Args:
            procesador: Implementación del procesador de pagos.
                       Si no se proporciona, usa la Factory para crearlo.
        """
        self._procesador = procesador or ProcesadorPagoFactory.crear()
        logger.info(
            'PagoService inicializado con procesador: %s',
            self._procesador.get_nombre()
        )

    def crear_pago(
        self,
        monto: float | str | Decimal,
        metodo_pago: str = 'tarjeta',
    ) -> Pago:
        """
        Crea un nuevo pago usando el Builder.
        
        Args:
            monto: Monto del pago.
            metodo_pago: Método de pago (tarjeta, transferencia, efectivo).
        
        Returns:
            Pago: Instancia del pago creado y guardado.
        
        Raises:
            ValidationError: Si los datos del pago no son válidos.
        """
        logger.info('Creando pago: monto=%s, metodo=%s', monto, metodo_pago)
        
        pago = (
            PagoBuilder()
            .con_monto(monto)
            .con_metodo_pago(metodo_pago)
            .build()
        )
        
        logger.info('Pago creado exitosamente: %s', pago.referencia)
        return pago

    def procesar_pago(self, pago: Pago) -> dict:
        """
        Procesa un pago existente.
        
        Cambia el estado del pago a EN_PROCESO y delega
        el procesamiento al procesador inyectado.
        
        Args:
            pago: Instancia del pago a procesar.
        
        Returns:
            dict: Resultado del procesamiento.
        
        Raises:
            ValidationError: Si la transición de estado no es válida.
            ValueError: Si el método de pago no está soportado.
        """
        logger.info('Iniciando procesamiento de pago: %s', pago.referencia)
        
        # Transicionar estado usando State Pattern del modelo
        pago._transicionar(pago.Estado.EN_PROCESO)
        
        # Delegar al procesador inyectado
        resultado = self._procesador.procesar(pago)
        
        logger.info(
            'Pago %s procesado: %s',
            pago.referencia,
            resultado.get('mensaje')
        )
        return resultado

    def confirmar_pago(self, pago: Pago) -> None:
        """Confirma un pago cambiando su estado a COMPLETADO."""
        logger.info('Confirmando pago: %s', pago.referencia)
        pago.confirmar_pago()

    def cancelar_pago(self, pago: Pago) -> None:
        """Cancela un pago."""
        logger.info('Cancelando pago: %s', pago.referencia)
        pago.cancelar_pago()


# ── Instancia global para uso simple ─────────────────────────────────
# Permite usar el servicio sin instanciarlo manualmente en las vistas

def get_pago_service(procesador: ProcesadorPagoBase | None = None) -> PagoService:
    """
    Factory function para obtener una instancia del servicio.
    
    Args:
        procesador: Procesador de pagos opcional (para inyección).
    
    Returns:
        PagoService: Instancia del servicio configurada.
    """
    return PagoService(procesador=procesador)
