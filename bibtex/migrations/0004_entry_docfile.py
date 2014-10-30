# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibtex', '0003_auto_20141013_2253'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='docfile',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
