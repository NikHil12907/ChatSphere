# Generated by Django 5.1.3 on 2025-01-12 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(default='default-avatar.jpg', upload_to='profile_pictures/'),
        ),
    ]
