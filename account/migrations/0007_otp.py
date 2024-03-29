# Generated by Django 3.2.5 on 2021-07-28 13:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_account_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.IntegerField(blank=True, null=True, verbose_name='OTP')),
                ('activation_key', models.CharField(blank=True, max_length=150, null=True, verbose_name='Activation Key')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'OTP',
                'verbose_name_plural': 'All OTP',
            },
        ),
    ]
