# Generated by Django 3.0.3 on 2020-05-03 05:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0021_auto_20200426_0110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fase',
            options={'permissions': (('create_item', 'Can create item'), ('aprove_item', 'Can aprove item'), ('modify_item', 'Can modify item'), ('unable_item', 'Can unable item'), ('reversionar_item', 'Reversionar item'), ('relacionar_item', 'Relacionar item'), ('change_item', 'Can change item'), ('establecer_itemPendienteAprob', 'Establecer ítem como pendiente de aprobación.'), ('establecer_itemDesarrollo', 'Establecer ítem como en desarrollo.'), ('obtener_trazabilidadItem', 'Obtener trazabilidad de ítem.'), ('ver_item', 'Visualizar ítem.'), ('deshabilitar_item', 'Deshabilitar Item'), ('obtener_calculoImpacto', 'Obtener cálculo de impacto de ítem.'), ('create_lineaBase', 'Crear Línea Base.'), ('break_lineaBase', 'Romper Línea Base.'), ('solicitar_roturaLineaBase', 'Solicitar rotura de línea base.'))},
        ),
    ]
