# Generated by Django 3.2.5 on 2021-07-22 02:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20210722_0228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilepicture',
            name='last_updated',
        ),
    ]
