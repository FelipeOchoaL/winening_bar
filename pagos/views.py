from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError

from pagos.models import Pago


def lista_pagos(request):
    """Listar todos los pagos."""
    pagos = Pago.objects.all()
    return render(request, 'pagos/lista_pagos.html', {'pagos': pagos})


def detalle_pago(request, pk):
    """Ver detalle de un pago."""
    pago = get_object_or_404(Pago, pk=pk)
    return render(request, 'pagos/detalle_pago.html', {'pago': pago})


def crear_pago(request):
    """Crear un nuevo pago."""
    if request.method == 'POST':
        monto = request.POST.get('monto')
        metodo_pago = request.POST.get('metodo_pago', 'tarjeta')

        if not monto:
            messages.error(request, 'El monto es requerido.')
            return render(request, 'pagos/crear_pago.html', {
                'metodos': Pago.MetodoPago.choices,
            })

        pago = Pago.objects.create(
            monto=monto,
            metodo_pago=metodo_pago,
        )
        messages.success(request, f'Pago creado con referencia {pago.referencia}')
        return redirect('pagos:detalle_pago', pk=pago.pk)

    return render(request, 'pagos/crear_pago.html', {
        'metodos': Pago.MetodoPago.choices,
    })


def procesar_pago(request, pk):
    """Procesar un pago (pasa a EN_PROCESO y ejecuta strategy)."""
    pago = get_object_or_404(Pago, pk=pk)
    try:
        resultado = pago.procesar_pago()
        messages.success(request, resultado['mensaje'])
    except (ValidationError, ValueError) as e:
        messages.error(request, str(e))
    return redirect('pagos:detalle_pago', pk=pago.pk)


def confirmar_pago(request, pk):
    """Confirmar un pago (pasa a COMPLETADO)."""
    pago = get_object_or_404(Pago, pk=pk)
    try:
        pago.confirmar_pago()
        messages.success(request, 'Pago confirmado exitosamente.')
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect('pagos:detalle_pago', pk=pago.pk)


def cancelar_pago(request, pk):
    """Cancelar un pago."""
    pago = get_object_or_404(Pago, pk=pk)
    try:
        pago.cancelar_pago()
        messages.warning(request, 'Pago cancelado.')
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect('pagos:detalle_pago', pk=pago.pk)
