from django.contrib import admin
from .models import Rol, Proyecto, FaseUser, TipodeItem, Fase, Item, Relacion, LineaBase, Files, ProyectoFase
from simple_history.admin import SimpleHistoryAdmin

class ProyectoHistoryAdmin(SimpleHistoryAdmin):
    history_list_display = ["tipoItem","nombre","campo_extra_valores","fecha","estado","observacion","costo","archivos", "relaciones"]
    search_fields = ['name', 'user__username']


admin.site.register(Fase)
admin.site.register(FaseUser)
admin.site.register(Files)
admin.site.register(Rol)
admin.site.register(Proyecto)
admin.site.register(TipodeItem)
admin.site.register(Relacion)
admin.site.register(LineaBase)
admin.site.register(Item,ProyectoHistoryAdmin)
admin.site.register(ProyectoFase)


