from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views import View

from pagos.models import Pago
from pagos.services import get_pago_service


class ListaPagosView(View):
    """Listar todos los pagos."""
    def get(self, request):
        pagos = Pago.objects.all()
        return render(request, 'pagos/lista_pagos.html', {'pagos': pagos})


class DetallePagoView(View):
    """Ver detalle de un pago."""
    def get(self, request, pk):
        pago = get_object_or_404(Pago, pk=pk)
        return render(request, 'pagos/detalle_pago.html', {'pago': pago})


class CrearPagoView(View):
    """Crear un nuevo pago delegando al Service Layer."""
    def get(self, request):
        return render(request, 'pagos/crear_pago.html', {
            'metodos': Pago.MetodoPago.choices,
        })

    def post(self, request):
        monto = request.POST.get('monto')
        metodo_pago = request.POST.get('metodo_pago', 'tarjeta')
        try:
            service = get_pago_service()
            pago = service.crear_pago(monto=monto, metodo_pago=metodo_pago)
            messages.success(request, f'Pago creado con referencia {pago.referencia}')
            return redirect('pagos:detalle_pago', pk=pago.pk)
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'pagos/crear_pago.html', {
                'metodos': Pago.MetodoPago.choices,
            })


class ProcesarPagoView(View):
    """Procesar un pago delegando al Service Layer."""
    def get(self, request, pk):
        pago = get_object_or_404(Pago, pk=pk)
        try:
            service = get_pago_service()
            resultado = service.procesar_pago(pago)
            messages.success(request, resultado['mensaje'])
        except (ValidationError, ValueError) as e:
            messages.error(request, str(e))
        return redirect('pagos:detalle_pago', pk=pago.pk)


class ConfirmarPagoView(View):
    """Confirmar un pago (pasa a COMPLETADO)."""
    def get(self, request, pk):
        pago = get_object_or_404(Pago, pk=pk)
        try:
            service = get_pago_service()
            service.confirmar_pago(pago)
            messages.success(request, 'Pago confirmado exitosamente.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('pagos:detalle_pago', pk=pago.pk)


class CancelarPagoView(View):
    """Cancelar un pago."""
    def get(self, request, pk):
        pago = get_object_or_404(Pago, pk=pk)
        try:
            service = get_pago_service()
            service.cancelar_pago(pago)
            messages.warning(request, 'Pago cancelado.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('pagos:detalle_pago', pk=pago.pk)
