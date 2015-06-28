# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibtex', '0007_auto_20150618_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='downloadurl',
            field=models.CharField(default=b'', max_length=200),
        ),
    ]
