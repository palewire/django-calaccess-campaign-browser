# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_campaign_browser', '0005_auto_20150115_0213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='date',
            field=models.DateField(default=None, null=True),
        ),
    ]
