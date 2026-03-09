"""
Excepciones de dominio para pagos.

Define excepciones específicas del negocio, separadas de las
excepciones genéricas de Django, para un manejo de errores
más expresivo y granular.
"""


class PagoError(Exception):
    """Excepción base para errores de dominio de pagos."""
    pass


class TransicionEstadoInvalidaError(PagoError):
    """Se intentó una transición de estado no permitida."""
    pass


class MetodoPagoNoSoportadoError(PagoError):
    """El método de pago no está soportado."""
    pass


class MontoInvalidoError(PagoError):
    """El monto del pago no es válido."""
    pass

