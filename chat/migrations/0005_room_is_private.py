# Generated by Django 5.1.3 on 2024-12-29 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_passwordresetotp'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
    ]
