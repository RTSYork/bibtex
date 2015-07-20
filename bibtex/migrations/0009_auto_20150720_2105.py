# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibtex', '0008_entry_downloadurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='downloadurl',
            field=models.CharField(default=b'', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='entry',
            name='html',
            field=models.TextField(default=b'', null=True),
        ),
        migrations.AlterField(
            model_name='entry',
            name='imgurl',
            field=models.CharField(default=b'', max_length=100, null=True),
        ),
    ]
