# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibtex', '0004_entry_docfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Docfile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('filename', models.CharField(max_length=100)),
                ('entry', models.ForeignKey(to='bibtex.Entry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='entry',
            name='docfile',
        ),
    ]
