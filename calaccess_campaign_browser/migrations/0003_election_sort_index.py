# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_campaign_browser', '0002_election_id_raw'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='sort_index',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
