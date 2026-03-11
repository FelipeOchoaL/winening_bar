"""
Excepciones de dominio para vinos y biblioteca.

Define excepciones específicas del negocio, separadas de las
excepciones genéricas de Django, para un manejo de errores
más expresivo y granular.
"""


class VinoError(Exception):
    """Excepción base para errores de dominio de vinos."""
    pass


class BibliotecaError(Exception):
    """Excepción base para errores de dominio de bibliotecas."""
    pass


class VinoRepetidoError(VinoError):
    """El vino ya existe en el sistema o en la biblioteca."""
    pass


class VinoNoEncontradoError(VinoError):
    """El vino no fue encontrado."""
    pass



