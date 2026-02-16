from django.urls import path

from pagos.views import (
    ListaPagosView,
    DetallePagoView,
    CrearPagoView,
    ProcesarPagoView,
    ConfirmarPagoView,
    CancelarPagoView,
)

app_name = 'pagos'

urlpatterns = [
    path('',                    ListaPagosView.as_view(),    name='lista_pagos'),
    path('crear/',              CrearPagoView.as_view(),     name='crear_pago'),
    path('<int:pk>/',           DetallePagoView.as_view(),   name='detalle_pago'),
    path('<int:pk>/procesar/',  ProcesarPagoView.as_view(),  name='procesar_pago'),
    path('<int:pk>/confirmar/', ConfirmarPagoView.as_view(), name='confirmar_pago'),
    path('<int:pk>/cancelar/',  CancelarPagoView.as_view(),  name='cancelar_pago'),
]
