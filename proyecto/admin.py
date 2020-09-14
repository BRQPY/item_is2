from django.contrib import admin

from .models import Rol, Proyecto, FaseUser, TipodeItem, Fase, Item
from simple_history.admin import SimpleHistoryAdmin

class ProyectoHistoryAdmin(SimpleHistoryAdmin):
    history_list_display = ["tipoItem","nombre","campo_extra_valores","fecha","estado","observacion","costo"]
    search_fields = ['name', 'user__username']


from .models import Rol, Proyecto, FaseUser, TipodeItem, Fase, Item, Relacion, LineaBase


admin.site.register(Fase)
admin.site.register(FaseUser)
admin.site.register(Rol)
admin.site.register(Proyecto,SimpleHistoryAdmin)
admin.site.register(TipodeItem)

admin.site.register(Item,ProyectoHistoryAdmin)





admin.site.register(Relacion)
admin.site.register(LineaBase)


