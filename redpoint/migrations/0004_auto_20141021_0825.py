# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('redpoint', '0003_room_beds_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bed',
            name='number',
            field=models.IntegerField(unique=True, blank=True, null=True),
        ),
    ]
