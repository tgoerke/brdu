# Generated by Django 2.2.2 on 2019-07-12 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fit', '0019_auto_20190710_1341'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='upload',
            name='user_filename',
        ),
    ]