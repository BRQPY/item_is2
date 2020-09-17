from django.contrib import admin
from .models import Rol, Proyecto, FaseUser, TipodeItem, Fase, Item, Relacion, LineaBase, Files, ProyectoFase
from simple_history.admin import SimpleHistoryAdmin


class ProyectoHistoryAdmin(SimpleHistoryAdmin):
    history_list_display = ["tipoItem", "nombre", "campo_extra_valores", "fecha", "estado", "observacion", "costo",
                            "archivos", "relaciones"]
    search_fields = ['name', 'user__username']


class ProyectoHistoryFase(SimpleHistoryAdmin):
    history_list_display = ["nombre", "descripcion", "estado", "items", "tipoItem", "lineasBase"]
    search_fields = ['name', 'user__username']


class ProyectoHistoryProyecto(SimpleHistoryAdmin):
    history_list_display = ["nombre", "descripcion", "fecha_inicio", "fecha_fin", "gerente", "creador", "estado",
                            "usuarios", "comite", "roles", "fases", "tipoItem"]
    search_fields = ['name', 'user__username']

class ProyectoHistoryProyectoFase(SimpleHistoryAdmin):
    history_list_display = ["proyecto", "fase"]
    search_fields = ['name', 'user__username']

class ProyectoHistoryRelacion(SimpleHistoryAdmin):
    history_list_display = ["tipo", "item_from","item_to"]
    search_fields = ['name', 'user__username']

admin.site.register(Fase, ProyectoHistoryFase)
admin.site.register(FaseUser)
admin.site.register(Files)
admin.site.register(Rol)
admin.site.register(Proyecto, ProyectoHistoryProyecto)
admin.site.register(TipodeItem)
admin.site.register(Relacion,ProyectoHistoryRelacion)
admin.site.register(LineaBase)
admin.site.register(Item, ProyectoHistoryAdmin)
admin.site.register(ProyectoFase,ProyectoHistoryProyectoFase)