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
from django.shortcuts import redirect

""""
def profile_view(request):
   ## usuario = User.objects.get(username = request.user.username)
   ## permiso = Permission.objects.get(codename = "add_user")
   ## usuario.user_permissions.add(permiso)
    return HttpResponse("Welcome %s <br> <a href='/accounts/logout/'>Logout</a>" % request.user.username)


def verif_view(request):
    grupo = Group.objects.get_or_create(name = 'Rol_x')
    usuario = User.objects.get(username=request.user.username)
    permiso = Permission.objects.get(codename = "view_menu")
    grupo = Group.objects.get(name = 'Rol_x')
    grupo.permissions.add(permiso)
    usuario.user_permissions.remove(permiso)
    #usuario.user_permissions.add(permiso)
    usuario.groups.add(grupo)
    #usuario.groups.remove(grupo)
    if usuario.has_perm("perms.view_menu"):
        return redirect("/accounts/profile/")
    return HttpResponse("Aun no cuenta con los permisos para acceder al sistema.")
"""

urlpatterns = [
    path('admin/', admin.site.urls),


]
