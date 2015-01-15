# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_campaign_browser', '0003_election_sort_index'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='election',
            options={'ordering': ('-sort_index',)},
        ),
        migrations.AlterModelOptions(
            name='office',
            options={'ordering': ('name', 'seat')},
        ),
        migrations.AddField(
            model_name='election',
            name='date',
            field=models.DateTimeField(default=datetime.date(2015, 1, 15)),
            preserve_default=False,
        ),
    ]
