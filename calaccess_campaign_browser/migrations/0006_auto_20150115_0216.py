# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_campaign_browser', '0005_auto_20150115_0130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposition',
            name='effective_date',
        ),
        migrations.RemoveField(
            model_name='proposition',
            name='status',
        ),
        migrations.RemoveField(
            model_name='proposition',
            name='xref_filer_id',
        ),
    ]
