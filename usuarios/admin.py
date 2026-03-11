from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from usuarios.models import Usuario, Suscripcion


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'nivel_catador', 'is_active')
    list_filter = ('nivel_catador', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Winening', {'fields': ('nivel_catador',)}),
    )


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'estado', 'fecha_inicio', 'fecha_fin')
    list_filter = ('estado', 'tipo')
    search_fields = ('usuario__username',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)



