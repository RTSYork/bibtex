# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibtex', '0006_entry_abstract'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='html',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='entry',
            name='imgurl',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
