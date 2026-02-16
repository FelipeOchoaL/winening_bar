"""
Builder Pattern — Construcción de objetos Pago de forma fluida y validada.

El PagoBuilder permite construir un objeto Pago paso a paso,
garantizando que sea válido antes de persistirlo en la base de datos.
Implementa Fluent Interface para encadenamiento de métodos.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from pagos.models import Pago


class PagoBuilder:
    """
    Builder para construir objetos Pago de manera fluida y segura.
    
    Uso:
        pago = (PagoBuilder()
            .con_monto(150.00)
            .con_metodo_pago('tarjeta')
            .build())
    """

    def __init__(self) -> None:
        self._monto: Decimal | None = None
        self._metodo_pago: str = 'tarjeta'
        self._errors: list[str] = []

    def con_monto(self, monto: float | str | Decimal) -> PagoBuilder:
        """Establece el monto del pago."""
        try:
            self._monto = Decimal(str(monto))
        except (InvalidOperation, ValueError):
            self._errors.append(f'Monto inválido: {monto}')
        return self

    def con_metodo_pago(self, metodo: str) -> PagoBuilder:
        """Establece el método de pago (tarjeta, transferencia, efectivo)."""
        from pagos.models import Pago
        metodos_validos = [choice[0] for choice in Pago.MetodoPago.choices]
        if metodo not in metodos_validos:
            self._errors.append(
                f'Método de pago inválido: {metodo}. '
                f'Opciones válidas: {metodos_validos}'
            )
        else:
            self._metodo_pago = metodo
        return self

    def _validar(self) -> None:
        """Valida que el objeto sea construible."""
        if self._monto is None:
            self._errors.append('El monto es requerido.')
        elif self._monto <= 0:
            self._errors.append('El monto debe ser mayor a cero.')

        if self._errors:
            raise ValidationError(self._errors)

    def build(self, save: bool = True) -> Pago:
        """
        Construye y retorna el objeto Pago.
        
        Args:
            save: Si es True, guarda el objeto en la base de datos.
                  Si es False, solo retorna la instancia sin persistir.
        
        Returns:
            Instancia de Pago validada.
        
        Raises:
            ValidationError: Si el objeto no es válido.
        """
        self._validar()

        from pagos.models import Pago
        pago = Pago(
            monto=self._monto,
            metodo_pago=self._metodo_pago,
        )

        if save:
            pago.full_clean()
            pago.save()

        return pago

