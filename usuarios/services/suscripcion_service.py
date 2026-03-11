"""
SuscripcionService — Orquestación de la lógica de negocio de suscripciones.

El servicio orquesta:
- Builder: Para construir objetos Suscripción válidos.
- Relación con Pagos: Genera pagos al crear suscripciones.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING

from usuarios.domain.builders import SuscripcionBuilder

if TYPE_CHECKING:
    from usuarios.models import Usuario, Suscripcion

logger = logging.getLogger(__name__)


class SuscripcionService:
    """
    Servicio de aplicación para operaciones de suscripciones.

    Uso:
        service = SuscripcionService()
        suscripcion = service.crear_suscripcion(usuario, tipo='mensual')
    """

    def crear_suscripcion(
        self,
        usuario: Usuario,
        tipo: str = 'mensual',
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
    ) -> Suscripcion:
        """
        Crea una nueva suscripción usando el Builder.

        Args:
            usuario: Usuario al que se asigna la suscripción.
            tipo: Tipo de suscripción (mensual, anual, prueba).
            fecha_inicio: Fecha de inicio (por defecto hoy).
            fecha_fin: Fecha de fin (calculada automáticamente si no se provee).

        Returns:
            Suscripcion: Instancia de la suscripción creada.

        Raises:
            ValidationError: Si los datos no son válidos.
        """
        logger.info(
            'Creando suscripción %s para usuario: %s',
            tipo, usuario.username,
        )

        suscripcion = (
            SuscripcionBuilder()
            .para_usuario(usuario)
            .con_tipo(tipo)
            .con_fechas(fecha_inicio, fecha_fin)
            .build()
        )

        logger.info(
            'Suscripción creada: %s (hasta %s)',
            suscripcion.get_tipo_display(),
            suscripcion.fecha_fin,
        )
        return suscripcion

    def cancelar_suscripcion(self, suscripcion: Suscripcion) -> None:
        """Cancela una suscripción activa."""
        logger.info('Cancelando suscripción: %s', suscripcion.pk)
        suscripcion.cancelar()

    def validar_acceso(self, suscripcion: Suscripcion) -> bool:
        """Valida si la suscripción permite acceso premium."""
        return suscripcion.validar_acceso()

    def listar_por_usuario(self, usuario: Usuario):
        """Lista todas las suscripciones de un usuario."""
        return usuario.suscripciones.all()


# ── Factory function ─────────────────────────────────────────────────

def get_suscripcion_service() -> SuscripcionService:
    """
    Factory function para obtener una instancia del servicio.

    Returns:
        SuscripcionService: Instancia del servicio configurada.
    """
    return SuscripcionService()



