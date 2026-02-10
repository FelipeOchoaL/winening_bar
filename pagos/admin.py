from django.contrib import admin

from pagos.models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display  = ('referencia', 'monto', 'metodo_pago', 'estado', 'created_at')
    list_filter   = ('estado', 'metodo_pago')
    search_fields = ('referencia',)
    readonly_fields = ('referencia', 'created_at', 'updated_at')
    ordering = ('-created_at',)
