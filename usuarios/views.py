from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views import View

from usuarios.models import Usuario, Suscripcion
from usuarios.services import get_usuario_service, get_suscripcion_service


class ListaUsuariosView(View):
    """Listar todos los usuarios."""
    def get(self, request):
        usuarios = Usuario.objects.all()
        return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


class DetalleUsuarioView(View):
    """Ver detalle de un usuario y sus suscripciones."""
    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        suscripciones = usuario.suscripciones.all()
        return render(request, 'usuarios/detalle_usuario.html', {
            'usuario': usuario,
            'suscripciones': suscripciones,
        })


class CrearUsuarioView(View):
    """Crear un nuevo usuario delegando al Service Layer."""
    def get(self, request):
        return render(request, 'usuarios/crear_usuario.html', {
            'niveles': Usuario.NivelCatador.choices,
        })

    def post(self, request):
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        nivel_catador = request.POST.get('nivel_catador', 'principiante')
        try:
            service = get_usuario_service()
            usuario = service.crear_usuario(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password or None,
                nivel_catador=nivel_catador,
            )
            messages.success(request, f'Usuario {usuario.username} creado exitosamente.')
            return redirect('usuarios:detalle_usuario', pk=usuario.pk)
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'usuarios/crear_usuario.html', {
                'niveles': Usuario.NivelCatador.choices,
            })


# ── Vistas de Suscripciones ─────────────────────────────────────────


class CrearSuscripcionView(View):
    """Crear una nueva suscripción para un usuario."""
    def get(self, request, usuario_pk):
        usuario = get_object_or_404(Usuario, pk=usuario_pk)
        return render(request, 'usuarios/crear_suscripcion.html', {
            'usuario': usuario,
            'tipos': Suscripcion.Tipo.choices,
        })

    def post(self, request, usuario_pk):
        usuario = get_object_or_404(Usuario, pk=usuario_pk)
        tipo = request.POST.get('tipo', 'mensual')
        try:
            service = get_suscripcion_service()
            suscripcion = service.crear_suscripcion(usuario=usuario, tipo=tipo)
            messages.success(
                request,
                f'Suscripción {suscripcion.get_tipo_display()} creada hasta {suscripcion.fecha_fin}.'
            )
            return redirect('usuarios:detalle_usuario', pk=usuario.pk)
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'usuarios/crear_suscripcion.html', {
                'usuario': usuario,
                'tipos': Suscripcion.Tipo.choices,
            })


class CancelarSuscripcionView(View):
    """Cancelar una suscripción activa."""
    def get(self, request, pk):
        suscripcion = get_object_or_404(Suscripcion, pk=pk)
        try:
            service = get_suscripcion_service()
            service.cancelar_suscripcion(suscripcion)
            messages.warning(request, 'Suscripción cancelada.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('usuarios:detalle_usuario', pk=suscripcion.usuario.pk)



