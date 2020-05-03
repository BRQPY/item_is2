from django.contrib import admin
from .models import Rol, Proyecto, FaseUser, TipodeItem, Fase, Item

admin.site.register(Fase)
admin.site.register(FaseUser)
admin.site.register(Rol)
admin.site.register(Proyecto)
admin.site.register(TipodeItem)
admin.site.register(Item)

