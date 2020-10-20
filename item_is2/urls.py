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
                cant = +1

        return render(request, "home.html", {'proyectos': proyectos, 'cant': cant, })
    return render(request, "wrong.html")


@login_required(login_url='/home/')
def permissionErrorView(request):
    return render(request, 'permissionError.html')



urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    path('permissionError/', permissionErrorView),
    path('home/', homeView, name="home"),
    path('gestionUser/Usuario/userid=<str:userid>/mensaje=<str:mensaje>/', viewsGestionUser.ConfigView, name="ConfigView"),
    path('gestionUser/mensaje=<str:mensaje>/', viewsGestionUser.gestionUserView, name="gestionUserView"),
    path('gestionUser/conf/userid=<str:userid>/', viewsGestionUser.confUserView, name='confUserView'),
    path('gestionUser/permisos/', viewsGestionUser.gestionPermsView, name='gestionPermsView'),
    path('gestionUser/permisos/agregar/', viewsGestionUser.addPermsView),
    path('gestionUser/permisos/remover/', viewsGestionUser.removePermsView),
    path('gestionUser/ver/', viewsGestionUser.verUserView, name="verUserView"),
    path('gestionUser/deshabilitar/userid=<str:userid>/', viewsGestionUser.unableUserView, name="unableUser"),
    path('gestionUser/habilitar/userid=<str:userid>/', viewsGestionUser.enableUserView, name="enableUser"),
    path('gestionUser/modify/', viewsGestionUser.changeUserView),
    path('proyecto/proyectoCrear/', views.proyectoCrear),
    path('proyecto/proyectoInicializar/proyectoid=<str:proyectoid>/', views.proyectoInicializar),
    path('proyecto/proyectoCancelar/proyectoid=<str:proyectoid>/', views.proyectoCancelar),
    path('proyecto/proyectoVer/proyectoid=<str:id>/', views.proyectoView, name="proyectoView"),
    path('proyecto/proyectoFase/proyectoid=<str:id>/', views.proyectoFase, name="proyectoFase"),
    path('proyecto/gestionProyecto/', views.gestionProyecto, name="ProyectoGestion"),
    path('proyecto/modify/', views.proyectoModificar),
    path('proyecto/unable/proyectoid=<str:proyectoid>/', views.proyectoDeshabilitar),
    path('proyecto/proyectoUser/', views.proyectoUser),
    path('proyecto/proyectoUser/add/', views.proyectoUserAdd),
    path('proyecto/proyectoUser/remove/proyectoid=<str:proyectoid>/userid=<str:userid>', views.proyectoUserRemove,
         name="ProyectoUserRemove"),
    path('proyecto/proyectoComite/proyectoid=<str:proyectoid>/mensaje=<str:mensaje>/', views.proyectoComite, name="Comite"),
    path('proyecto/proyectoComite/add/', views.proyectoComiteAdd, name="ComiteAdd"),
    path('proyecto/proyectoComite/remove/proyectoid=<str:proyectoid>/userid=<str:userid>/', views.proyectoComiteRemove, name="ComiteRemove"),
    path('proyecto/proyectoRol/proyectoid=<str:proyectoid>/mensaje=<str:mensaje>/', views.proyectoRol, name="ProyectoRol"),
    path('proyecto/proyectoRol/create/', views.proyectoRolCrear),
    path('proyecto/proyectoRol/modify/proyectoid=<str:proyectoid>/rolid=<str:rolid>/', views.proyectoRolModificar,
         name="ProyectoRolModify"),
    path('proyecto/proyectoRol/delete/proyectoid=<str:proyectoid>/rolid=<str:rolid>/', views.proyectoRolEliminar,
         name="ProyectoRolRemove"),
    path('fase/faseVer/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', views.faseView, name="faseView"),
    path('proyecto/proyectoTipodeItem/', views.gestionar_tipo_de_item, name="gestionTipoItem"),
    path('proyecto/creartipo/', views.crear_tipo_form, name="creartipo"),
    path('proyecto/modifdeItem/proyectoid=<str:proyectoid>/tipoid=<str:tipoid>/', views.modificar_tipo_de_item,
         name="modificartipo"),
    path('proyecto/importTdeItem/', views.importar_tipo_de_item, name="importartipo"),
    path('proyecto/proyectoremoverTdeItem/proyectoid=<str:proyectoid>/tipoid=<str:tipoid>/', views.remover_tipo_de_item,
         name="removertipo"),
    path('fase/faseCrear/', viewsFase.faseCrear),
    path('fase/faseUsers/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', viewsFase.faseUsers, name="faseUsers"),
    path('fase/gestionFase/', viewsFase.gestionFase),
    path('fase/modify/', viewsFase.faseModificar),
    path('fase/unable/proyectoid=<str:proyectoid>/', viewsFase.faseDeshabilitar),
    path('fase/asignarRol/proyectoid=<str:proyectoid>/faseid=<str:faseid>/userid=<str:userid>',
         viewsFase.faseRolAsignar, name="faseRolAsignar"),
    path('fase/removerRol/proyectoid=<str:proyectoid>/faseid=<str:faseid>/userid=<str:userid>',
         viewsFase.faseRolRemover, name="faseRolRemover"),
    path('fase/removerUser/proyectoid=<str:proyectoid>/faseid=<str:faseid>/userid=<str:userid>',
         viewsFase.FaseRemoveUser, name="faseRemoverUser"),
    path('fase/FaseProyectoInicializado/faseid=<str:faseid>/proyectoid=<str:proyectoid>/mensaje=<str:mensaje>',
         viewsFase.faseVerProyectoInicializado, name="faseViewInicializado"),
    path('fase/FaseIniciada/config/proyectoid=<str:proyectoid>/faseid=<str:faseid>/', viewsFase.FaseConfigInicializada, name="faseConfinicializada"),
    path('fase/addUser/', viewsFase.FaseAddUser),
    path('fase/gestionTipoItem/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', viewsFase.FaseGestionTipoItem,
         name="faseTipoItem"),
    path('fase/addTipoItem/', viewsFase.FaseAddTipoItem),
    path('fase/ConfigLineaBase/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>', viewsFase.faseConfigLineaBase, name="faseConfigLineaBase"),
    path('fase/gestionLineaBase/proyectoid=<str:proyectoid>/faseid=<str:faseid>/mensaje=<str:mensaje>/', viewsFase.faseGestionLineaBase, name="LineaBase"),
    path('fase/consultarLineaBase/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/', viewsFase.consultarLineaBase, name="consultarLineaBase"),
    path('fase/addLineaBase/', viewsFase.faseAddLineaBase),
    path('fase/lineaBaseAddItem/', viewsFase.lineaBaseAddItem),
    path('fase/lineaBaseRemoveItem/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/itemid=<str:itemid>/',
         viewsFase.lineaBaseRemoveItem, name="lineaBaseRemoveItem"),
    path('fase/cerrarLineaBase/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/', viewsFase.faseCerrarLineaBase, name="lineaBaseCerrar"),
    path('fase/RemoveTipoItem/proyectoid=<str:proyectoid>/faseid=<str:faseid>/tipoid=<str:tipoid>', viewsFase.FaseRemoveTipoItem, name="faseRemoveTipo"),
    path('fase/fasesDeshabilitadas/', viewsFase.fasesDeshabilitadas),
    path('item/gestionItem/', viewsFase.gestionItem),
    path('item/configurar/itemid=<str:itemid>/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', viewsFase.itemConfigurar, name="itemConfigurar"),
    path('item/itemVer/itemid=<int:itemid>/faseid=<int:faseid>/proyectoid=<int:proyectoid>/', viewsFase.itemView, name="itemView"),
    path('item/itemCrear/', viewsFase.itemCrear),
    path('item/modify/', viewsFase.itemModificar),
    path('item/itemCambiarEstado/', viewsFase.itemCambiarEstado),
    path('item/unable/proyectoid=<str:proyectoid>/faseid=<int:faseid>/itemid=<int:itemid>/', viewsFase.itemDeshabilitar),
    path('item/relaciones/ver/itemid=<str:itemid>/faseid=<str:faseid>/proyectoid=<str:proyectoid>/mensaje=<str:mensaje>/',viewsFase.itemVerRelaciones, name="itemVerRelaciones"),
    path('item/relaciones/remover/itemid=<str:itemid>/item_rm=<str:item_rm>/faseid=<str:faseid>/proyectoid=<str:proyectoid>/',viewsFase.itemRelacionesRemover, name="itemRelacionesRemover"),
    path('item/addRelacion/', viewsFase.itemAddRelacion),
    path('item/history/', viewsFase.itemHistorial, name="itemHistorial"),
    path(
        'item/history/reversionar/proyecto<int:proyectoid>/faseid<int:faseid>/itemid<int:itemid>/history_data<str:history_date>/',
        viewsFase.itemReversionar, name="itemRev"),
    path('item/relaciones/ver/itemid=<str:itemid>/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', viewsFase.itemVerRelaciones, name="itemVerRelaciones"),
    path('item/relaciones/remover/itemid=<str:itemid>/item_rm=<str:item_rm>/faseid=<str:faseid>/proyectoid=<str:proyectoid>/',viewsFase.itemRelacionesRemover, name="itemRelacionesRemover"),
    path('item/downloadFile/filename=<str:filename>/itemid=<str:itemid>/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', viewsFase.downloadFile, name="download"),
    path('fase/cerrarFase/proyectoid=<str:proyectoid>/faseid=<str:faseid>/',viewsFase.cerrarFase, name="cerrarFaseView"),
    path('item/calculoImpacto/',viewsFase.itemCalculoImpacto),
    path('fase/roturaLineaBase/listado/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/mensaje=<str:mensaje>/',
         viewsFase.gestionRoturaLineaBase, name="gestionRoturaLineaBase"),
    path('fase/roturaLineaBase/form/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/',
         viewsFase.formRoturaLineaBase, name="formRoturaLineaBase"),
    path('fase/roturaLineaBase/votacion/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/solicituid=<str:solicituid>/',
         viewsFase.votacionRoturaLineaBase, name="votacionRoturaLineaBase"),
    path('fase/roturaLineaBase/votacion/aprobado/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/solicituid=<str:solicituid>/',
         viewsFase.AprobarRoturaLineaBase, name="AprobarRoturaLineaBase"),
    path('fase/roturaLineaBase/votacion/rechazado/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/solicituid=<str:solicituid>/',
         viewsFase.RechazarRoturaLineaBase, name="RechazarRoturaLineaBase"),
    path('fase/roturaLineaBase/comprometida/listado/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/',
         viewsFase.gestionRoturaLineaBaseComprometida, name="gestionRoturaLineaBaseComprometida"),
    path('fase/roturaLineaBase/comprometida/votacion/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/',
         viewsFase.votacionRoturaLineaBaseComprometida, name="votacionRoturaLineaBaseComprometida"),
    path('fase/roturaLineaBase/comprometida/votacion/aprobado/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/solicituid=<str:solicituid>/',
         viewsFase.AprobarRoturaLineaBaseComprometida, name="AprobarRoturaLineaBaseComprometida"),
    path('fase/roturaLineaBase/comprometida/votacion/rechazado/proyectoid=<str:proyectoid>/faseid=<str:faseid>/lineaBaseid=<str:lineaBaseid>/solicituid=<str:solicituid>/',
         viewsFase.RechazarRoturaLineaBaseComprometida, name="RechazarRoturaLineaBaseComprometida"),
    path('item/trazabilidad/',viewsFase.itemTrazabilidad),
    path('item/verDatos/itemid=<str:itemid>/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', viewsFase.itemVerDatos, name="itemVerDatos"),
    path('item/SolicitudCambio/itemid=<str:itemid>/faseid=<str:faseid>/proyectoid=<str:proyectoid>/', viewsFase.solicitarCambioEstado, name="SolicitudCambio"),
    path('proyecto/finalizar/proyectoid=<str:proyectoid>/', views.ProyectoFinalizar, name="ProyectoFinalizar"),
]
