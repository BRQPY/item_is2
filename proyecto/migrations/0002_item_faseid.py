# Generated by Django 3.0.3 on 2020-10-10 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='faseid',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
