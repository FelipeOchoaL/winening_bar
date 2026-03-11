"""
API Views DRF — Capa de presentación REST para Usuarios y Suscripciones.

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

from usuarios.models import Usuario, Suscripcion
from usuarios.serializers import (
    UsuarioSerializer,
    CrearUsuarioSerializer,
    SuscripcionSerializer,
    CrearSuscripcionSerializer,
)
from usuarios.services import get_usuario_service, get_suscripcion_service


# ── Usuarios ────────────────────────────────────────────────────────


class UsuarioListAPIView(APIView):
    """
    GET /api/usuarios/
    Lista todos los usuarios del sistema.
    """

    def get(self, request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsuarioDetailAPIView(APIView):
    """
    GET /api/usuarios/<pk>/
    Retorna el detalle de un usuario específico.
    """

    def get(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': f'Usuario con id {pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsuarioCreateAPIView(APIView):
    """
    POST /api/usuarios/crear/
    Crea un nuevo usuario delegando al Service Layer.

    Body JSON:
        {
            "username": "juan",
            "email": "juan@email.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "password": "secreto123",
            "nivel_catador": "intermedio"
        }

    Responses:
        201: Usuario creado exitosamente.
        400: Datos de entrada inválidos.
        409: El username ya existe (conflicto).
    """

    def post(self, request):
        serializer = CrearUsuarioSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verificar si el username ya existe
        if Usuario.objects.filter(
            username=serializer.validated_data['username']
        ).exists():
            return Response(
                {'error': f'El usuario "{serializer.validated_data["username"]}" ya existe.'},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            service = get_usuario_service()
            usuario = service.crear_usuario(
                username=serializer.validated_data['username'],
                email=serializer.validated_data.get('email', ''),
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                password=serializer.validated_data.get('password'),
                nivel_catador=serializer.validated_data['nivel_catador'],
            )

            output = UsuarioSerializer(usuario)
            return Response(output.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'errors': e.messages if hasattr(e, 'messages') else [str(e)]},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── Suscripciones ───────────────────────────────────────────────────


class SuscripcionListAPIView(APIView):
    """
    GET /api/usuarios/<usuario_pk>/suscripciones/
    Lista las suscripciones de un usuario.
    """

    def get(self, request, usuario_pk):
        try:
            usuario = Usuario.objects.get(pk=usuario_pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': f'Usuario con id {usuario_pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = get_suscripcion_service()
        suscripciones = service.listar_por_usuario(usuario)
        serializer = SuscripcionSerializer(suscripciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SuscripcionCreateAPIView(APIView):
    """
    POST /api/usuarios/<usuario_pk>/suscripciones/crear/
    Crea una nueva suscripción para un usuario.

    Body JSON:
        {
            "tipo": "mensual"
        }

    Responses:
        201: Suscripción creada exitosamente.
        400: Datos de entrada inválidos.
        404: Usuario no encontrado.
    """

    def post(self, request, usuario_pk):
        try:
            usuario = Usuario.objects.get(pk=usuario_pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': f'Usuario con id {usuario_pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CrearSuscripcionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = get_suscripcion_service()
            suscripcion = service.crear_suscripcion(
                usuario=usuario,
                tipo=serializer.validated_data['tipo'],
            )

            output = SuscripcionSerializer(suscripcion)
            return Response(output.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'errors': e.messages if hasattr(e, 'messages') else [str(e)]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SuscripcionCancelarAPIView(APIView):
    """
    POST /api/usuarios/suscripciones/<pk>/cancelar/
    Cancela una suscripción activa.

    Responses:
        200: Suscripción cancelada.
        404: Suscripción no encontrada.
        409: Transición de estado inválida.
    """

    def post(self, request, pk):
        try:
            suscripcion = Suscripcion.objects.get(pk=pk)
        except Suscripcion.DoesNotExist:
            return Response(
                {'error': f'Suscripción con id {pk} no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            service = get_suscripcion_service()
            service.cancelar_suscripcion(suscripcion)
            output = SuscripcionSerializer(suscripcion)
            return Response(output.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_409_CONFLICT,
            )

