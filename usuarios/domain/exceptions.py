"""
Excepciones de dominio para usuarios y suscripciones.

Define excepciones específicas del negocio, separadas de las
excepciones genéricas de Django, para un manejo de errores
más expresivo y granular.
"""


class UsuarioError(Exception):
    """Excepción base para errores de dominio de usuarios."""
    pass


class SuscripcionError(Exception):
    """Excepción base para errores de dominio de suscripciones."""
    pass


class TransicionEstadoSuscripcionError(SuscripcionError):
    """Se intentó una transición de estado no permitida en la suscripción."""
    pass


class SuscripcionExpiradaError(SuscripcionError):
    """La suscripción ha expirado y no permite la operación."""
    pass



