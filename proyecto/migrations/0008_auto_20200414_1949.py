# Generated by Django 3.0.3 on 2020-04-14 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0007_remove_item_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='fecha',
            field=models.CharField(default=None, max_length=40),
        ),
    ]
