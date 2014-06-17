#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

try:
   import pypandoc
   description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   description = open('README.md').read()


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-calaccess-browser',
    version='0.2.2',
    packages=[
        'campaign_finance',
        'campaign_finance.management',
        'campaign_finance.management.commands',
	'campaign_finance.utils',
    ],
    include_package_data=True,
    license='MIT License',  # example license
    description='A simple Django app browse California campaign finance data from Cal-Access.',
    long_description=description,
    url='https://github.com/california-civic-data-coalition',
    author='Agustin Armendariz, Aaron Williams',
    author_email='awilliams@cironline.org',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],

    install_requires=[
        #'django-calaccess-parser==0.1',
    ],
    # dependency_links=[
    #     'git+ssh://git@github.com:california-civic-data-coalition/django-calaccess-parser.git@0.1#egg-django-calaccess-parser-0.1'
    # ]
)
