# Generated by Django 3.1.2 on 2020-11-27 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20201127_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(default='courses/default.jpg', upload_to='courses/'),
        ),
    ]