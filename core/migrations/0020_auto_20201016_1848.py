# Generated by Django 2.0 on 2020-10-16 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20201016_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='percentage',
            field=models.FloatField(default=0),
        ),
    ]
