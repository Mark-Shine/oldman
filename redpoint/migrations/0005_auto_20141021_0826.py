# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('redpoint', '0004_auto_20141021_0825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bed',
            name='number',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
