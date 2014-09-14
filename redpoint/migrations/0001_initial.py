# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bed',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Oldman',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=16, verbose_name='姓名', blank=True, null=True)),
                ('time', models.DateTimeField(blank=True, null=True)),
                ('avatar', models.ImageField(upload_to='avatars', verbose_name='照片')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('floor', models.IntegerField(blank=True, null=True)),
                ('room_number', models.IntegerField(blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bed',
            name='room',
            field=models.ForeignKey(blank=True, null=True, to='redpoint.Room'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bed',
            name='who',
            field=models.ForeignKey(blank=True, null=True, to='redpoint.Oldman'),
            preserve_default=True,
        ),
    ]
