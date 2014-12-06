# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('redpoint', '0005_auto_20141021_0826'),
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('payload', models.TextField(blank=True, null=True)),
                ('create', models.DateTimeField(null=True, auto_now_add=True)),
                ('start_t', models.DateTimeField(blank=True, null=True)),
                ('end_t', models.DateTimeField(blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='bed',
            options={'ordering': ('id',)},
        ),
    ]
