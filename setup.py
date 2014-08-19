#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
from distutils.core import Command


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(
            DATABASES={
                'default': {
                    'NAME': ':memory:',
                    'ENGINE': 'django.db.backends.sqlite3'
                }
            },
            INSTALLED_APPS=('calaccess_campaign_browser',)
        )
        from django.core.management import call_command
        call_command('test', 'calaccess_campaign_browser')

setup(
    name='django-calaccess-campaign-browser',
    version='0.0.2',
    packages=[
        'calaccess_campaign_browser',
        'calaccess_campaign_browser.management',
        'calaccess_campaign_browser.management.commands',
        'calaccess_campaign_browser.utils',
    ],
    include_package_data=True,
    license='MIT',
    description='A Django app to refine and investigate campaign finance data \
drawn from the California Secretary of State’s CAL-ACCESS database',
    url='https://github.com/california-civic-data-coalition',
    author='California Civic Data Coalition',
    author_email='awilliams@cironline.org',
    install_requires=(
        'django-calaccess-raw-data>=0.0.2',
        'django>=1.6',
        'csvkit==0.6.1',
        'python-dateutil==2.1',
        'MySQL-python==1.2.5',
        'argparse==1.2.1',
        'requests==2.2.1',
        'progressbar>=2.2',
        'hurry.filesize==0.9',
    ),
    cmdclass={'test': TestCommand}
)
