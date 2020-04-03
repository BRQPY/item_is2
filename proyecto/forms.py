
from django import forms
from .models import Proyecto

class ProyectoForm(forms.ModelForm):


    class Meta:
        model = Proyecto
        fields = (

            'nombre',
            'fecha_inicio',
            'fecha_fin',
            'descripcion',
            'gerente',
        )
