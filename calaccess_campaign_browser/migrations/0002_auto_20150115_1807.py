# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_campaign_browser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'ordering': ('election', 'office', 'filer'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, choices=[(b'GENERAL', b'General'), (b'PRIMARY', b'Primary'), (b'RECALL', b'Recall'), (b'SPECIAL', b'Special'), (b'SPECIAL_RUNOFF', b'Special Runoff'), (b'OTHER', b'Other')])),
                ('year', models.IntegerField()),
                ('date', models.DateField(default=None, null=True)),
                ('id_raw', models.IntegerField(help_text=b'The unique identifer from the CAL-ACCESS site', verbose_name=b'UID (CAL-ACCESS)')),
                ('sort_index', models.IntegerField(help_text=b'The order of the election specified on the CAL-ACCESS site')),
            ],
            options={
                'ordering': ('-sort_index',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, choices=[(b'ASSEMBLY', b'Assembly'), (b'ATTORNEY_GENERAL', b'Attorney General'), (b'BOARD_OF_EQUALIZATION', b'Board of Equalization'), (b'CONTROLLER', b'Controller'), (b'GOVERNOR', b'Governor'), (b'INSURANCE_COMMISSIONER', b'Insurance Commissioner'), (b'LIEUTENANT_GOVERNOR', b'Lieutenant Governor'), (b'OTHER', b'Other'), (b'SECRETARY_OF_STATE', b'Secretary of State'), (b'SENATE', b'Senate'), (b'SUPERINTENDENT_OF_PUBLIC_INSTRUCTION', b'Superintendent of Public Instruction'), (b'TREASURER', b'Treasurer')])),
                ('seat', models.IntegerField(default=None, null=True)),
            ],
            options={
                'ordering': ('name', 'seat'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Proposition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('filer_id_raw', models.IntegerField(db_index=True)),
                ('election', models.ForeignKey(default=None, to='calaccess_campaign_browser.Election', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
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
        migrations.AddField(
            model_name='proposition',
            name='filers',
            field=models.ManyToManyField(to='calaccess_campaign_browser.Filer', through='calaccess_campaign_browser.PropositionFiler'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidate',
            name='election',
            field=models.ForeignKey(to='calaccess_campaign_browser.Election'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidate',
            name='filer',
            field=models.ForeignKey(to='calaccess_campaign_browser.Filer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidate',
            name='office',
            field=models.ForeignKey(to='calaccess_campaign_browser.Office'),
            preserve_default=True,
        ),
    ]
