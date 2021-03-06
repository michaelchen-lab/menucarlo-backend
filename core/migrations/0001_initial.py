# Generated by Django 3.1.4 on 2020-12-14 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
                ('business_name', models.CharField(max_length=100)),
                ('source', models.CharField(choices=[('Square', 'Square'), ('Unknown', 'Unknown')], max_length=100)),
                ('raw_data', models.FileField(upload_to='')),
                ('parsed_data', models.FileField(upload_to='')),
            ],
        ),
    ]
