from django.urls import path

from pagos import views

app_name = 'pagos'

urlpatterns = [
    path('',                    views.lista_pagos,    name='lista_pagos'),
    path('crear/',              views.crear_pago,     name='crear_pago'),
    path('<int:pk>/',           views.detalle_pago,   name='detalle_pago'),
    path('<int:pk>/procesar/',  views.procesar_pago,  name='procesar_pago'),
    path('<int:pk>/confirmar/', views.confirmar_pago, name='confirmar_pago'),
    path('<int:pk>/cancelar/',  views.cancelar_pago,  name='cancelar_pago'),
]

