# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibtex', '0005_auto_20141014_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='abstract',
            field=models.TextField(default=b''),
        ),
    ]
