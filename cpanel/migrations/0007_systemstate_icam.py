# Generated by Django 3.0.5 on 2020-05-10 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpanel', '0006_remove_event_video_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemstate',
            name='icam',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
