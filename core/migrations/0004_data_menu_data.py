# Generated by Django 3.1.4 on 2020-12-17 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20201216_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='menu_data',
            field=models.FileField(default=[], upload_to=''),
            preserve_default=False,
        ),
    ]
