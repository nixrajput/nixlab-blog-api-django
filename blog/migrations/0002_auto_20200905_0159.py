# Generated by Django 3.1.1 on 2020-09-04 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True, verbose_name='Slug'),
        ),
    ]
