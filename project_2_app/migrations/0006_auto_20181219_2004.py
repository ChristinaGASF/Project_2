# Generated by Django 2.0.5 on 2018-12-19 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_2_app', '0005_auto_20181219_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='thumbnail_height',
            field=models.CharField(default='', max_length=4),
        ),
        migrations.AlterField(
            model_name='video',
            name='thumbnail_width',
            field=models.CharField(default='', max_length=4),
        ),
    ]