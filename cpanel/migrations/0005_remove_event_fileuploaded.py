# Generated by Django 3.0.5 on 2020-05-10 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cpanel', '0004_auto_20200510_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='fileUploaded',
        ),
    ]
