# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gwstore', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='weight_lb',
            field=models.DecimalField(blank=True, max_digits=16, null=True, decimal_places=2),
        ),
    ]
