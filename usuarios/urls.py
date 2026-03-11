from django.urls import path

from usuarios.views import (
    ListaUsuariosView,
    DetalleUsuarioView,
    CrearUsuarioView,
    CrearSuscripcionView,
    CancelarSuscripcionView,
)
from usuarios.api_views import (
    UsuarioListAPIView,
    UsuarioDetailAPIView,
    UsuarioCreateAPIView,
    SuscripcionListAPIView,
    SuscripcionCreateAPIView,
    SuscripcionCancelarAPIView,
)

app_name = 'usuarios'

urlpatterns = [
    # ── Vistas HTML (Templates) ─────────────────────────────────────
    path('',                                ListaUsuariosView.as_view(),      name='lista_usuarios'),
    path('crear/',                          CrearUsuarioView.as_view(),       name='crear_usuario'),
    path('<int:pk>/',                       DetalleUsuarioView.as_view(),     name='detalle_usuario'),
    path('<int:usuario_pk>/suscripcion/',   CrearSuscripcionView.as_view(),   name='crear_suscripcion'),
    path('suscripcion/<int:pk>/cancelar/',  CancelarSuscripcionView.as_view(), name='cancelar_suscripcion'),

    # ── API REST (DRF) ─────────────────────────────────────────────
    path('api/',                                      UsuarioListAPIView.as_view(),       name='api_lista_usuarios'),
    path('api/crear/',                                UsuarioCreateAPIView.as_view(),     name='api_crear_usuario'),
    path('api/<int:pk>/',                             UsuarioDetailAPIView.as_view(),     name='api_detalle_usuario'),
    path('api/<int:usuario_pk>/suscripciones/',       SuscripcionListAPIView.as_view(),   name='api_lista_suscripciones'),
    path('api/<int:usuario_pk>/suscripciones/crear/', SuscripcionCreateAPIView.as_view(), name='api_crear_suscripcion'),
    path('api/suscripciones/<int:pk>/cancelar/',      SuscripcionCancelarAPIView.as_view(), name='api_cancelar_suscripcion'),
]
