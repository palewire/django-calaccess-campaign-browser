#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
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
            INSTALLED_APPS=('calaccess_campaign_browser',),
            MIDDLEWARE_CLASSES=()
        )
        from django.core.management import call_command
        import django
        if django.VERSION[:2] >= (1, 7):
            django.setup()
        call_command('test', 'calaccess_campaign_browser')


setup(
    name='django-calaccess-campaign-browser',
    version='0.1.1',
    license='MIT',
    description='A Django app to refine and investigate campaign finance data \
drawn from the California Secretary of State’s CAL-ACCESS database. \
This is a work in progress. Its analysis should be considered as \
provisional until it is further tested and debugged.',
    url='http://django-calaccess-campaign-browser.californiacivicdata.org',
    author='California Civic Data Coalition',
    author_email='awilliams@cironline.org',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,  # because we're including static files
    install_requires=(
        'django-calaccess-raw-data>=0.1.2',
        'django>=1.6',
        'csvkit>=0.6.1',
        'python-dateutil==2.2',
        'MySQL-python>=1.2.5',
        'hurry.filesize>=0.9',
        'django-tastypie>=0.11.1',
        'beautifulsoup4>=4.3.2',
    ),
    cmdclass={'test': TestCommand,}
)
