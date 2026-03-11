from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views import View

from vinos.models import Vino, BibliotecaVinos
from vinos.services import get_biblioteca_service


class ListaVinosView(View):
    """Listar todos los vinos del catálogo."""
    def get(self, request):
        vinos = Vino.objects.all()
        return render(request, 'vinos/lista_vinos.html', {'vinos': vinos})


class DetalleVinoView(View):
    """Ver detalle de un vino."""
    def get(self, request, pk):
        vino = get_object_or_404(Vino, pk=pk)
        perfil = vino.calcular_perfil_sensorial()
        return render(request, 'vinos/detalle_vino.html', {
            'vino': vino,
            'perfil': perfil,
        })


class CrearVinoView(View):
    """Crear un nuevo vino delegando al Service Layer."""
    def get(self, request):
        return render(request, 'vinos/crear_vino.html')

    def post(self, request):
        nombre = request.POST.get('nombre', '').strip()
        variedad = request.POST.get('variedad', '').strip()
        anio = request.POST.get('anio', '')
        region = request.POST.get('region', '').strip()
        try:
            service = get_biblioteca_service()
            vino = service.crear_vino(
                nombre=nombre,
                variedad=variedad,
                anio=anio,
                region=region,
            )
            messages.success(request, f'Vino "{vino.nombre}" creado exitosamente.')
            return redirect('vinos:detalle_vino', pk=vino.pk)
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'vinos/crear_vino.html')


class BibliotecaUsuarioView(View):
    """Ver la biblioteca de vinos de un usuario."""
    def get(self, request, usuario_pk):
        from usuarios.models import Usuario
        usuario = get_object_or_404(Usuario, pk=usuario_pk)
        service = get_biblioteca_service()
        biblioteca = service.obtener_o_crear_biblioteca(usuario)
        vinos_biblioteca = biblioteca.listar_vinos()
        vinos_disponibles = Vino.objects.exclude(pk__in=vinos_biblioteca.values_list('pk', flat=True))
        return render(request, 'vinos/biblioteca.html', {
            'usuario': usuario,
            'biblioteca': biblioteca,
            'vinos_biblioteca': vinos_biblioteca,
            'vinos_disponibles': vinos_disponibles,
        })


class AgregarVinoView(View):
    """Agregar un vino a la biblioteca de un usuario."""
    def get(self, request, usuario_pk, vino_pk):
        from usuarios.models import Usuario
        usuario = get_object_or_404(Usuario, pk=usuario_pk)
        vino = get_object_or_404(Vino, pk=vino_pk)
        try:
            service = get_biblioteca_service()
            service.agregar_vino_a_biblioteca(usuario, vino)
            messages.success(request, f'Vino "{vino.nombre}" agregado a tu biblioteca.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('vinos:biblioteca', usuario_pk=usuario.pk)


class RemoverVinoView(View):
    """Remover un vino de la biblioteca de un usuario."""
    def get(self, request, usuario_pk, vino_pk):
        from usuarios.models import Usuario
        usuario = get_object_or_404(Usuario, pk=usuario_pk)
        vino = get_object_or_404(Vino, pk=vino_pk)
        try:
            service = get_biblioteca_service()
            service.remover_vino_de_biblioteca(usuario, vino)
            messages.warning(request, f'Vino "{vino.nombre}" removido de tu biblioteca.')
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('vinos:biblioteca', usuario_pk=usuario.pk)



