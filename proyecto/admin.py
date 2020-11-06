from django.contrib import admin
from .models import Rol, Proyecto, FaseUser, TipodeItem, Fase, Item, Relacion, LineaBase, Files, ProyectoFase, RoturaLineaBase, RoturaLineaBaseComprometida, ActaInforme, SolicitudCambioEstado
from reversion.admin import VersionAdmin



class YourModelAdmin(VersionAdmin):

    history_latest_first: True
    list_display = ["tipoItem", "nombre", "campo_extra_valores", "fecha", "estado", "observacion", "costo",
                    "archivos"]


class YourModelAdminRelaciones(VersionAdmin):
    history_latest_first:True


class YourModelAdminFase(VersionAdmin):
    history_latest_first:True

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
