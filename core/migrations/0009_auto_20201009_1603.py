# Generated by Django 2.0 on 2020-10-09 16:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20201009_1457'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='Ordered',
            new_name='is_ordered',
        ),
    ]