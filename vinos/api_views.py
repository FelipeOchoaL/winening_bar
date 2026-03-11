"""
API Views DRF — Capa de presentación REST para Vinos y Biblioteca.

Cada APIView se limita a:
1. Validar la entrada con Serializers.
2. Delegar la lógica al Service Layer.
3. Serializar la salida y retornar la respuesta con el código HTTP adecuado.

NO contienen lógica de negocio (cumplimiento SOLID — SRP).
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import ValidationError

from vinos.models import Vino, BibliotecaVinos
from vinos.serializers import (
    VinoSerializer,
    CrearVinoSerializer,
    BibliotecaVinosSerializer,
)
from vinos.services import get_biblioteca_service


# ── Vinos (Catálogo) ────────────────────────────────────────────────


class VinoListAPIView(APIView):
    """
    GET /api/vinos/
    Lista todos los vinos del catálogo.
    """

    def get(self, request):
        service = get_biblioteca_service()
        vinos = service.listar_todos_los_vinos()
        serializer = VinoSerializer(vinos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VinoDetailAPIView(APIView):
    """
    GET /api/vinos/<pk>/
    Retorna el detalle de un vino con su perfil sensorial.
    """

    def get(self, request, pk):
        try:
            vino = Vino.objects.get(pk=pk)
        except Vino.DoesNotExist:
            return Response(
                {'error': f'Vino con id {pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = VinoSerializer(vino)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VinoCreateAPIView(APIView):
    """
    POST /api/vinos/crear/
    Crea un nuevo vino en el catálogo delegando al Service Layer.

    Body JSON:
        {
            "nombre": "Catena Zapata",
            "variedad": "Malbec",
            "anio": 2020,
            "region": "Mendoza"
        }

    Responses:
        201: Vino creado exitosamente.
        400: Datos de entrada inválidos.
        409: El vino ya existe (repetido).
    """

    def post(self, request):
        serializer = CrearVinoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = get_biblioteca_service()
            vino = service.crear_vino(
                nombre=serializer.validated_data['nombre'],
                variedad=serializer.validated_data['variedad'],
                anio=serializer.validated_data['anio'],
                region=serializer.validated_data['region'],
            )

            # Verificar duplicado
            if vino.es_vino_repetido():
                return Response(
                    {'error': f'Ya existe un vino similar: {vino.nombre} ({vino.variedad}, {vino.anio}).'},
                    status=status.HTTP_409_CONFLICT,
                )

            output = VinoSerializer(vino)
            return Response(output.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'errors': e.messages if hasattr(e, 'messages') else [str(e)]},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── Biblioteca de Vinos ─────────────────────────────────────────────


class BibliotecaAPIView(APIView):
    """
    GET /api/vinos/biblioteca/<usuario_pk>/
    Retorna la biblioteca de vinos de un usuario.
    """

    def get(self, request, usuario_pk):
        from usuarios.models import Usuario

        try:
            usuario = Usuario.objects.get(pk=usuario_pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': f'Usuario con id {usuario_pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = get_biblioteca_service()
        biblioteca = service.obtener_o_crear_biblioteca(usuario)
        serializer = BibliotecaVinosSerializer(biblioteca)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BibliotecaAgregarVinoAPIView(APIView):
    """
    POST /api/vinos/biblioteca/<usuario_pk>/agregar/<vino_pk>/
    Agrega un vino a la biblioteca personal de un usuario.

    Responses:
        200: Vino agregado exitosamente.
        404: Usuario o vino no encontrado.
        409: El vino ya está en la biblioteca (conflicto).
    """

    def post(self, request, usuario_pk, vino_pk):
        from usuarios.models import Usuario

        try:
            usuario = Usuario.objects.get(pk=usuario_pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': f'Usuario con id {usuario_pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            vino = Vino.objects.get(pk=vino_pk)
        except Vino.DoesNotExist:
            return Response(
                {'error': f'Vino con id {vino_pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            service = get_biblioteca_service()
            service.agregar_vino_a_biblioteca(usuario, vino)
            biblioteca = service.obtener_o_crear_biblioteca(usuario)
            serializer = BibliotecaVinosSerializer(biblioteca)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_409_CONFLICT,
            )


class BibliotecaRemoverVinoAPIView(APIView):
    """
    POST /api/vinos/biblioteca/<usuario_pk>/remover/<vino_pk>/
    Remueve un vino de la biblioteca personal de un usuario.

    Responses:
        200: Vino removido exitosamente.
        404: Usuario o vino no encontrado.
        409: El vino no está en la biblioteca.
    """

    def post(self, request, usuario_pk, vino_pk):
        from usuarios.models import Usuario

        try:
            usuario = Usuario.objects.get(pk=usuario_pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': f'Usuario con id {usuario_pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            vino = Vino.objects.get(pk=vino_pk)
        except Vino.DoesNotExist:
            return Response(
                {'error': f'Vino con id {vino_pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            service = get_biblioteca_service()
            service.remover_vino_de_biblioteca(usuario, vino)
            biblioteca = service.obtener_o_crear_biblioteca(usuario)
            serializer = BibliotecaVinosSerializer(biblioteca)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_409_CONFLICT,
            )

