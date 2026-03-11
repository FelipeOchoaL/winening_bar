from django.urls import path

from vinos.views import (
    ListaVinosView,
    DetalleVinoView,
    CrearVinoView,
    BibliotecaUsuarioView,
    AgregarVinoView,
    RemoverVinoView,
)
from vinos.api_views import (
    VinoListAPIView,
    VinoDetailAPIView,
    VinoCreateAPIView,
    BibliotecaAPIView,
    BibliotecaAgregarVinoAPIView,
    BibliotecaRemoverVinoAPIView,
)

app_name = 'vinos'

urlpatterns = [
    # ── Vistas HTML (Templates) ─────────────────────────────────────
    path('',                                         ListaVinosView.as_view(),        name='lista_vinos'),
    path('crear/',                                   CrearVinoView.as_view(),         name='crear_vino'),
    path('<int:pk>/',                                DetalleVinoView.as_view(),       name='detalle_vino'),
    path('biblioteca/<int:usuario_pk>/',             BibliotecaUsuarioView.as_view(), name='biblioteca'),
    path('biblioteca/<int:usuario_pk>/agregar/<int:vino_pk>/',  AgregarVinoView.as_view(),  name='agregar_vino'),
    path('biblioteca/<int:usuario_pk>/remover/<int:vino_pk>/',  RemoverVinoView.as_view(),  name='remover_vino'),

    # ── API REST (DRF) ─────────────────────────────────────────────
    path('api/',                                                   VinoListAPIView.as_view(),             name='api_lista_vinos'),
    path('api/crear/',                                             VinoCreateAPIView.as_view(),           name='api_crear_vino'),
    path('api/<int:pk>/',                                          VinoDetailAPIView.as_view(),           name='api_detalle_vino'),
    path('api/biblioteca/<int:usuario_pk>/',                       BibliotecaAPIView.as_view(),           name='api_biblioteca'),
    path('api/biblioteca/<int:usuario_pk>/agregar/<int:vino_pk>/', BibliotecaAgregarVinoAPIView.as_view(), name='api_agregar_vino'),
    path('api/biblioteca/<int:usuario_pk>/remover/<int:vino_pk>/', BibliotecaRemoverVinoAPIView.as_view(), name='api_remover_vino'),
]
