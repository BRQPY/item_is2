"""prueba URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.models import User
from django.shortcuts import render
from gestionUser.views import gestionUserView, confUserView, changeUserView, gestionPermsView, addPermsView, removePermsView, verUserView, unableUserView
from proyecto.models import Proyecto
#from proyecto.views import proyectoTipodeItem, proyectoCrear, proyectoView, gestionProyecto, proyectoModificar, proyectoDeshabilitar, proyectoUser, proyectoUserAdd, proyectoUserRemove, proyectoComite, proyectoComiteAdd, proyectoComiteRemove, proyectoRol, proyectoRolAsignar, proyectoRolRemover, proyectoRolCrear, proyectoRolModificar, proyectoRolEliminar, faseView
from django.contrib.auth.decorators import login_required
from proyecto import views
#from TipodeItem import views
from django.conf import settings
from django.conf.urls.static import static

@login_required
def homeView(request):
    usuario = User.objects.get(id=request.user.id)
    if usuario.has_perm("perms.view_menu"):
        proyectos = Proyecto.objects.filter(usuarios__id=request.user.id)
        cant = 0
        for p in proyectos:
            if not p.estado == "deshabilitado":
                cant=+1

        return render(request, "home.html", {'proyectos': proyectos, 'cant': cant, })
    return render(request, "wrong.html")


@login_required(login_url='/home/')
def permissionErrorView(request):
    return render(request, 'permissionError.html')


urlpatterns = []
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root= settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root= settings.MEDIA_ROOT)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    path('permissionError/', permissionErrorView),
    path('home/', homeView),
    path('gestionUser/', gestionUserView, name="gestionUserView"),
    #url(r'^gestionUser/', gestionUserView, name="gestionUser"),
    path('gestionUser/conf/', confUserView, name='confUserView'),
    path('gestionUser/permisos/', gestionPermsView, name='gestionPermsView'),
    path('gestionUser/permisos/agregar/', addPermsView),
    path('gestionUser/permisos/remover/', removePermsView),
    path('gestionUser/ver/', verUserView, name="verUserView"),
    path('gestionUser/deshabilitar/', unableUserView),
    path('gestionUser/modify/', changeUserView),
    #path('proyecto/', include(('proyecto.urls', 'proyecto'))),
    path('proyecto/proyectoCrear/', views.proyectoCrear),
    path('proyecto/proyectoVer/<str:id>/', views.proyectoView, name="proyectoView"),
    path('proyecto/gestionProyecto/', views.gestionProyecto),
    path('proyecto/modify/', views.proyectoModificar),
    path('proyecto/unable/', views.proyectoDeshabilitar),
    path('proyecto/proyectoUser/', views.proyectoUser),
    path('proyecto/proyectoUser/add/', views.proyectoUserAdd),
    path('proyecto/proyectoUser/remove/', views.proyectoUserRemove),
    path('proyecto/proyectoComite/', views.proyectoComite),
    path('proyecto/proyectoComite/add/', views.proyectoComiteAdd),
    path('proyecto/proyectoComite/remove/', views.proyectoComiteRemove),
    path('proyecto/proyectoRol/', views.proyectoRol),
    path('proyecto/proyectoRol/create/', views.proyectoRolCrear),
    path('proyecto/proyectoRol/modify/', views.proyectoRolModificar),
    path('proyecto/proyectoRol/asignar/', views.proyectoRolAsignar),
    path('proyecto/proyectoRol/remove/', views.proyectoRolRemover),
    path('proyecto/proyectoRol/delete/', views.proyectoRolEliminar),
    path('fase/faseVer/<str:faseid><str:proyectoid>/', views.faseView, name="faseView"),
    path('proyecto/proyectoTipodeItem/', views.gestionar_tipo_de_item),
    path('proyecto/creartipo/', views.crear_tipo_form, name="creartipo"),
    path('proyecto/modifdeItem/', views.modificar_tipo_de_item, name="modificartipo"),
    path('proyecto/importTdeItem/', views.importar_tipo_de_item, name="importartipo"),
    path('proyecto/removerTdeItem/', views.remover_tipo_de_item, name="removertipo"),
]

