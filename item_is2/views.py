from django.shortcuts import render, redirect

def login_prueba(request):
    return render(request, 'login.html')

def bienvenido(request):
    return render(request, 'login_Aprobado.html')