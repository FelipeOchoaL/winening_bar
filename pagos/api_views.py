"""
API Views DRF — Capa de presentación REST para Pagos.

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

from pagos.models import Pago
from pagos.serializers import PagoSerializer, CrearPagoSerializer
from pagos.services import get_pago_service


class PagoListAPIView(APIView):
    """
    GET /api/pagos/
    Lista todos los pagos del sistema.
    """

    def get(self, request):
        pagos = Pago.objects.all()
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PagoDetailAPIView(APIView):
    """
    GET /api/pagos/<pk>/
    Retorna el detalle de un pago específico.
    """

    def get(self, request, pk):
        try:
            pago = Pago.objects.get(pk=pk)
        except Pago.DoesNotExist:
            return Response(
                {'error': f'Pago con id {pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PagoSerializer(pago)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PagoCreateAPIView(APIView):
    """
    POST /api/pagos/crear/
    Crea un nuevo pago delegando al Service Layer.

    Body JSON:
        {
            "monto": 150.00,
            "metodo_pago": "tarjeta"
        }

    Responses:
        201: Pago creado exitosamente.
        400: Datos de entrada inválidos.
    """

    def post(self, request):
        serializer = CrearPagoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = get_pago_service()
            pago = service.crear_pago(
                monto=serializer.validated_data['monto'],
                metodo_pago=serializer.validated_data['metodo_pago'],
            )

            output = PagoSerializer(pago)
            return Response(output.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'errors': e.messages if hasattr(e, 'messages') else [str(e)]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PagoProcesarAPIView(APIView):
    """
    POST /api/pagos/<pk>/procesar/
    Procesa un pago existente (PENDIENTE → EN_PROCESO).

    Responses:
        200: Pago procesado exitosamente.
        404: Pago no encontrado.
        409: Transición de estado inválida (conflicto).
    """

    def post(self, request, pk):
        try:
            pago = Pago.objects.get(pk=pk)
        except Pago.DoesNotExist:
            return Response(
                {'error': f'Pago con id {pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            service = get_pago_service()
            resultado = service.procesar_pago(pago)
            return Response(resultado, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_409_CONFLICT,
            )


class PagoConfirmarAPIView(APIView):
    """
    POST /api/pagos/<pk>/confirmar/
    Confirma un pago (EN_PROCESO → COMPLETADO).

    Responses:
        200: Pago confirmado.
        404: Pago no encontrado.
        409: Transición de estado inválida.
    """

    def post(self, request, pk):
        try:
            pago = Pago.objects.get(pk=pk)
        except Pago.DoesNotExist:
            return Response(
                {'error': f'Pago con id {pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            service = get_pago_service()
            service.confirmar_pago(pago)
            output = PagoSerializer(pago)
            return Response(output.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_409_CONFLICT,
            )


class PagoCancelarAPIView(APIView):
    """
    POST /api/pagos/<pk>/cancelar/
    Cancela un pago.

    Responses:
        200: Pago cancelado.
        404: Pago no encontrado.
        409: Transición de estado inválida.
    """

    def post(self, request, pk):
        try:
            pago = Pago.objects.get(pk=pk)
        except Pago.DoesNotExist:
            return Response(
                {'error': f'Pago con id {pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            service = get_pago_service()
            service.cancelar_pago(pago)
            output = PagoSerializer(pago)
            return Response(output.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_409_CONFLICT,
            )

