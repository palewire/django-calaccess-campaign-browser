# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_campaign_browser', '0004_auto_20150115_0127'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proposition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('filer_id_raw', models.IntegerField(db_index=True)),
                ('xref_filer_id', models.CharField(max_length=32, null=True, db_index=True)),
                ('status', models.CharField(max_length=255, null=True, choices=[(b'A', b'Active'), (b'ACTIVE', b'Active'), (b'INACTIVE', b'Inactive'), (b'N', b'Inactive'), (b'P', b'Pending'), (b'R', b'Revoked'), (b'S', b'Suspended'), (b'TERMINATED', b'Terminated'), (b'W', b'Withdrawn'), (b'Y', b'Active')])),
                ('effective_date', models.DateField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='election',
            name='id_raw',
            field=models.IntegerField(help_text=b'The unique identifer from the CAL-ACCESS site', verbose_name=b'UID (CAL-ACCESS)'),
        ),
        migrations.AlterField(
            model_name='election',
            name='sort_index',
            field=models.IntegerField(help_text=b'The order of the election specified on the CAL-ACCESS site'),
        ),
        migrations.AlterField(
            model_name='office',
            name='name',
            field=models.CharField(max_length=50, choices=[(b'ASSEMBLY', b'Assembly'), (b'ATTORNEY_GENERAL', b'Attorney General'), (b'BOARD_OF_EQUALIZATION', b'Board of Equalization'), (b'CONTROLLER', b'Controller'), (b'GOVERNOR', b'Governor'), (b'INSURANCE_COMMISSIONER', b'Insurance Commissioner'), (b'LIEUTENANT_GOVERNOR', b'Lieutenant Governor'), (b'OTHER', b'Other'), (b'SECRETARY_OF_STATE', b'Secretary of State'), (b'SENATE', b'Senate'), (b'SUPERINTENDENT_OF_PUBLIC_INSTRUCTION', b'Superintendent of Public Instruction'), (b'TREASURER', b'Treasurer')]),
        ),
    ]
