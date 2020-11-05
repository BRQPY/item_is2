from django.contrib import admin
from .models import Rol, Proyecto, FaseUser, TipodeItem, Fase, Item, Relacion, LineaBase, Files, ProyectoFase, RoturaLineaBase, RoturaLineaBaseComprometida, ActaInforme, SolicitudCambioEstado

import reversion
from reversion.admin import VersionAdmin



class YourModelAdmin(VersionAdmin):

    history_latest_first: True
    list_display = ["tipoItem", "nombre", "campo_extra_valores", "fecha", "estado", "observacion", "costo",
                    "archivos"]
    reversion.register(follow=['relaciones'])

class YourModelAdminRelaciones(VersionAdmin):
    history_latest_first:True


class YourModelAdminFase(VersionAdmin):
    history_latest_first:True


"""
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
"""
admin.site.register(Fase, YourModelAdminFase )
admin.site.register(FaseUser)
admin.site.register(Files)
admin.site.register(Rol)
admin.site.register(Proyecto)
admin.site.register(TipodeItem)
admin.site.register(Relacion,YourModelAdminRelaciones)
admin.site.register(LineaBase)
admin.site.register(RoturaLineaBase)
admin.site.register(RoturaLineaBaseComprometida)
admin.site.register(ProyectoFase)
admin.site.register(Item, YourModelAdmin)
admin.site.register(ActaInforme)
admin.site.register(SolicitudCambioEstado)
