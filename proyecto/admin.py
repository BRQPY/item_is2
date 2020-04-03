
from django.contrib import admin
from .models import Fase, Rol, Proyecto, FaseUser, TipodeItem


admin.site.register(Fase)
admin.site.register(FaseUser)
admin.site.register(Rol)
admin.site.register(Proyecto)
admin.site.register(TipodeItem)

