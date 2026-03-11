from django.contrib import admin

from vinos.models import Vino, BibliotecaVinos, NotaSensorial


@admin.register(Vino)
class VinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'variedad', 'anio', 'region')
    list_filter = ('variedad', 'region')
    search_fields = ('nombre', 'variedad', 'region')
    ordering = ('nombre',)


@admin.register(BibliotecaVinos)
class BibliotecaVinosAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_creacion', 'cantidad_vinos')
    search_fields = ('usuario__username',)

    def cantidad_vinos(self, obj):
        return obj.vinos.count()
    cantidad_vinos.short_description = 'Vinos'


@admin.register(NotaSensorial)
class NotaSensorialAdmin(admin.ModelAdmin):
    list_display = ('vino', 'aroma', 'color', 'sabor', 'textura', 'created_at')
    list_filter = ('vino',)
    readonly_fields = ('created_at',)



