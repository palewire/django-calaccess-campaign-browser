# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_campaign_browser', '0008_proposition_election'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropositionFiler',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.CharField(max_length=50, choices=[(b'SUPPORT', b'Support'), (b'OPPOSE', b'Oppose')])),
                ('filer', models.ForeignKey(to='calaccess_campaign_browser.Filer')),
                ('proposition', models.ForeignKey(to='calaccess_campaign_browser.Proposition')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='candidate',
            options={'ordering': ('election', 'office', 'filer')},
        ),
        migrations.AddField(
            model_name='proposition',
            name='filers',
            field=models.ManyToManyField(to='calaccess_campaign_browser.Filer', through='calaccess_campaign_browser.PropositionFiler'),
            preserve_default=True,
        ),
    ]
