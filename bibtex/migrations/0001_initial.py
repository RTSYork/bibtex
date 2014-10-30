# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('owner', models.CharField(max_length=50)),
                ('key', models.CharField(max_length=50)),
                ('entered', models.DateTimeField(verbose_name='date entered')),
                ('bib', models.CharField(max_length=1000)),
                ('year', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
