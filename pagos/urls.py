from django.urls import path

from pagos.views import (
    ListaPagosView,
    DetallePagoView,
    CrearPagoView,
    ProcesarPagoView,
    ConfirmarPagoView,
    CancelarPagoView,
)
from pagos.api_views import (
    PagoListAPIView,
    PagoDetailAPIView,
    PagoCreateAPIView,
    PagoProcesarAPIView,
    PagoConfirmarAPIView,
    PagoCancelarAPIView,
)

app_name = 'pagos'

urlpatterns = [
    # ── Vistas HTML (Templates) ─────────────────────────────────────
    path('',                    ListaPagosView.as_view(),    name='lista_pagos'),
    path('crear/',              CrearPagoView.as_view(),     name='crear_pago'),
    path('<int:pk>/',           DetallePagoView.as_view(),   name='detalle_pago'),
    path('<int:pk>/procesar/',  ProcesarPagoView.as_view(),  name='procesar_pago'),
    path('<int:pk>/confirmar/', ConfirmarPagoView.as_view(), name='confirmar_pago'),
    path('<int:pk>/cancelar/',  CancelarPagoView.as_view(),  name='cancelar_pago'),

    # ── API REST (DRF) ─────────────────────────────────────────────
    path('api/',                    PagoListAPIView.as_view(),      name='api_lista_pagos'),
    path('api/crear/',              PagoCreateAPIView.as_view(),    name='api_crear_pago'),
    path('api/<int:pk>/',           PagoDetailAPIView.as_view(),    name='api_detalle_pago'),
    path('api/<int:pk>/procesar/',  PagoProcesarAPIView.as_view(),  name='api_procesar_pago'),
    path('api/<int:pk>/confirmar/', PagoConfirmarAPIView.as_view(), name='api_confirmar_pago'),
    path('api/<int:pk>/cancelar/',  PagoCancelarAPIView.as_view(),  name='api_cancelar_pago'),
]
