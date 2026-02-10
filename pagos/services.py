"""
Strategy Pattern — cada método de pago implementa su propia lógica
de procesamiento a través de una función estrategia.

Se registran en el diccionario ESTRATEGIAS y PagoService.procesar()
delega automáticamente según el metodo_pago del objeto Pago.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pagos.models import Pago

logger = logging.getLogger(__name__)


# ── Estrategias concretas ──────────────────────────────────────────

def _procesar_tarjeta(pago: Pago) -> dict:
    """Lógica específica para pago con tarjeta."""
    logger.info('Procesando pago %s con tarjeta — $%s', pago.referencia, pago.monto)
    # Aquí iría la integración con pasarela de pago (Stripe, MercadoPago, etc.)
    return {
        'exito': True,
        'mensaje': f'Pago con tarjeta procesado correctamente (ref: {pago.referencia})',
        'metodo': 'tarjeta',
    }


def _procesar_transferencia(pago: Pago) -> dict:
    """Lógica específica para pago por transferencia bancaria."""
    logger.info('Procesando pago %s por transferencia — $%s', pago.referencia, pago.monto)
    return {
        'exito': True,
        'mensaje': f'Transferencia registrada, pendiente de verificación (ref: {pago.referencia})',
        'metodo': 'transferencia',
    }


def _procesar_efectivo(pago: Pago) -> dict:
    """Lógica específica para pago en efectivo."""
    logger.info('Procesando pago %s en efectivo — $%s', pago.referencia, pago.monto)
    return {
        'exito': True,
        'mensaje': f'Pago en efectivo registrado (ref: {pago.referencia})',
        'metodo': 'efectivo',
    }


# ── Registro de estrategias (Strategy registry) ───────────────────

ESTRATEGIAS = {
    'tarjeta':       _procesar_tarjeta,
    'transferencia': _procesar_transferencia,
    'efectivo':      _procesar_efectivo,
}


# ── Servicio principal ────────────────────────────────────────────

class PagoService:
    """
    Punto de entrada para procesar pagos.
    Selecciona la estrategia adecuada según el método de pago.
    """

    @staticmethod
    def procesar(pago: Pago) -> dict:
        estrategia = ESTRATEGIAS.get(pago.metodo_pago)
        if estrategia is None:
            raise ValueError(
                f'Método de pago no soportado: {pago.metodo_pago}'
            )
        return estrategia(pago)

