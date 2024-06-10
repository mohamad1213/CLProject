# Generated by Django 5.0.6 on 2024-06-09 17:40

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_profile_user_delete_customuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='users/profile_pics/default.png', upload_to=users.models.user_profile_pic_path),
        ),
    ]
