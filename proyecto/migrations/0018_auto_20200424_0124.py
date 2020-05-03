# Generated by Django 3.0.3 on 2020-04-24 01:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0017_auto_20200423_1729'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={'ordering': ['nombre'], 'permissions': (('is_gerente', 'Can do anything in project'), ('inicialize_proyecto', 'Can inicialize proyecto'), ('cancel_proyecto', 'Can cancel proyecto'), ('create_tipoItem', 'Crear tipo de item'), ('import_tipoItem', 'Importar tipo de item'), ('view_tipoItem', 'Visualizar tipo de ítem.'), ('change_tipoItem', 'Modificar tipo de item'), ('delete_tipoItem', 'Eliminar tipo de item'), ('add_miembros', 'Can add miembros'), ('delete_miembros', 'Can delete miembros'), ('view_miembros', 'Can view miembros'), ('create_rol', 'Can create rol'), ('change_rol', 'Can change rol'), ('delete_rol', 'Can delete rol'), ('view_rol', 'Can view rol'), ('assign_rol', 'Can assign rol'), ('remove_rol', 'Can remove rol'), ('create_comite', 'Can create comite'), ('change_comite', 'Can change comite'), ('view_comite', 'Can view_comite comite'), ('aprobar_rotura_lineaBase', 'Romper Línea Base.')), 'verbose_name': 'Proyecto', 'verbose_name_plural': 'Proyectos'},
        ),
    ]
