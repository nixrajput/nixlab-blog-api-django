# Generated by Django 3.2.5 on 2021-08-18 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_alter_postimage_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='title',
        ),
        migrations.AddField(
            model_name='blogpost',
            name='content',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Content'),
        ),
    ]
