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
from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.models import User
from django.shortcuts import render
from proyecto.models import Proyecto
from django.contrib.auth.decorators import login_required
from proyecto import views
from fase import views as viewsFase
from gestionUser import views as viewsGestionUser
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
    path('home/', homeView, name="home"),
    path('gestionUser/', viewsGestionUser.gestionUserView, name="gestionUserView"),
    path('gestionUser/conf/', viewsGestionUser.confUserView, name='confUserView'),
    path('gestionUser/permisos/', viewsGestionUser.gestionPermsView, name='gestionPermsView'),
    path('gestionUser/permisos/agregar/', viewsGestionUser.addPermsView),
    path('gestionUser/permisos/remover/', viewsGestionUser.removePermsView),
    path('gestionUser/ver/', viewsGestionUser.verUserView, name="verUserView"),
    path('gestionUser/deshabilitar/', viewsGestionUser.unableUserView),
    path('gestionUser/habilitar/', viewsGestionUser.enableUserView),
    path('gestionUser/modify/', viewsGestionUser.changeUserView),
    path('proyecto/proyectoCrear/', views.proyectoCrear),
    path('proyecto/proyectoInicializar/', views.proyectoInicializar),
    path('proyecto/proyectoCancelar/', views.proyectoCancelar),
    path('proyecto/proyectoVer/proyectoid=<str:id>/', views.proyectoView, name="proyectoView"),
    path('proyecto/proyectoFase/proyectoid=<str:id>/', views.proyectoFase, name="proyectoFase"),
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
    path('proyecto/proyectoRol/delete/', views.proyectoRolEliminar),
    path('fase/faseVer/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', views.faseView, name="faseView"),
    path('proyecto/proyectoTipodeItem/', views.gestionar_tipo_de_item),
    path('proyecto/creartipo/', views.crear_tipo_form, name="creartipo"),
    path('proyecto/modifdeItem/', views.modificar_tipo_de_item, name="modificartipo"),
    path('proyecto/importTdeItem/', views.importar_tipo_de_item, name="importartipo"),
    path('proyecto/proyectoremoverTdeItem/', views.remover_tipo_de_item, name="removertipo"),
    path('fase/faseCrear/', viewsFase.faseCrear),
    path('fase/gestionFase/', viewsFase.gestionFase),
    path('fase/modify/', viewsFase.faseModificar),
    path('fase/unable/', viewsFase.faseDeshabilitar),
    path('fase/asignarRol/proyectoid=<str:proyectoid>/faseid=<str:faseid>/userid=<str:userid>', viewsFase.faseRolAsignar, name="faseRolAsignar"),
    path('fase/removerRol/proyectoid=<str:proyectoid>/faseid=<str:faseid>/userid=<str:userid>', viewsFase.faseRolRemover, name="faseRolRemover"),
    path('fase/removerUser/proyectoid=<str:proyectoid>/faseid=<str:faseid>/userid=<str:userid>', viewsFase.FaseRemoveUser, name="faseRemoverUser"),
    path('fase/FaseProyectoInicializado/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', viewsFase.faseVerProyectoInicializado, name="faseViewInicializado"),
    path('fase/FaseIniciada/config/', viewsFase.FaseConfigInicializada),
    path('fase/addUser/', viewsFase.FaseAddUser),
    path('fase/gestionTipoItem/', viewsFase.FaseGestionTipoItem, name="faseTipoItem"),
    path('fase/addTipoItem/', viewsFase.FaseAddTipoItem),
    path('fase/RemoveTipoItem/proyectoid=<str:proyectoid>/faseid=<str:faseid>/tipoid=<str:tipoid>', viewsFase.FaseRemoveTipoItem, name="faseRemoveTipo"),
    path('fase/fasesDeshabilitadas/', viewsFase.fasesDeshabilitadas),
    path('item/gestionItem/', viewsFase.gestionItem),
    path('item/itemVer/itemid=<int:itemid>faseid=<int:faseid>proyectoid=<int:proyectoid>/', viewsFase.itemView, name="itemView"),
    path('item/itemCrear/', viewsFase.itemCrear),
    path('item/modify/', viewsFase.itemModificar),
    path('item/itemCambiarEstado/', viewsFase.itemCambiarEstado),
    path('item/unable/', viewsFase.itemDeshabilitar),
]