# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-05 04:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0003_auto_20170205_0321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='twitch',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='twitter',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
