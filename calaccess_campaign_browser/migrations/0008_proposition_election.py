# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_campaign_browser', '0007_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposition',
            name='election',
            field=models.ForeignKey(default=None, to='calaccess_campaign_browser.Election', null=True),
            preserve_default=True,
        ),
    ]
