===================
Management commands
===================

Loaders
=======

buildcalaccesscampaignbrowser
-----------------------------

The master command that runs all of the other commands below necessary to completely
update the database.

.. code-block:: bash

    Usage: example/manage.py buildcalaccesscampaignbrowser [options] 

    Transforms and loads refined data from raw CAL-ACCESS source files

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit


loadcalaccesscampaigncontributions
----------------------------------

.. code-block:: bash

    Usage: example/manage.py loadcalaccesscampaigncontributions [options]

    Load refined campaign contributions from CAL-ACCESS raw data

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit


loadcalaccesscampaignexpenditures
---------------------------------

.. code-block:: bash

    Usage: example/manage.py loadcalaccesscampaignexpenditures [options] 

    Load refined campaign expenditures from CAL-ACCESS raw data

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit


loadcalaccesscampaignfilers
---------------------------

.. code-block:: bash

    Usage: example/manage.py loadcalaccesscampaignfilers [options] 

    Load refined CAL-ACCESS campaign filers and committees

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit


loadcalaccesscampaignfilings
----------------------------

.. code-block:: bash

    Usage: example/manage.py loadcalaccesscampaignfilings [options] 

    Load refined CAL-ACCESS campaign filings

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --flush               Flush table before loading data
      --version             show program's version number and exit
      -h, --help            show this help message and exit


loadcalaccesscampaignsummaries
------------------------------

.. code-block:: bash

    Usage: example/manage.py loadcalaccesscampaignsummaries [options] 

    Load refined CAL-ACCESS campaign filing summaries

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit


Exporters
=========

exportcalaccesscampaignbrowser
------------------------------

.. code-block:: bash

    Usage: example/manage.py exportcalaccesscampaignbrowser [options] 

    Export refined CAL-ACCESS campaign browser data as CSV files

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --skip-contributions  Skip contributions export
      --skip-expenditures   Skip expenditures export
      --skip-summary        Skip summary export
      --version             show program's version number and exit
      -h, --help            show this help message and exit


Scrapers
========

scrapecalaccesscampaigncandidates
---------------------------------

.. code-block:: bash

    Usage: example/manage.py scrapecalaccesscampaigncandidates [options] 

    Scrape links between filers and elections from the CAL-ACCESS site

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit


scrapecalaccesscampaignpropositions
-----------------------------------

.. code-block:: bash

    Usage: example/manage.py scrapecalaccesscampaignpropositions [options] 

    Scrape links between filers and propositions from the CAL-ACCESS site

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit


scrapecalaccesscampaignelectiondates
------------------------------------

.. code-block:: bash

    Usage: example/manage.py scrapecalaccesscampaignelectiondates [options] 

    Scrape election dates from the Secretary of State's site

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit


Other
=====

dropcalaccesscampaignbrowser
----------------------------

.. code-block:: bash

    Usage: example/manage.py dropcalaccesscampaignbrowser [options] 

    Drops all CAL-ACCESS campaign browser database tables

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit


flushcalaccesscampaignbrowser
-----------------------------

.. code-block:: bash

    Usage: example/manage.py flushcalaccesscampaignbrowser [options] 

    Flush CAL-ACCESS campaign browser database tables

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on exception
      --no-color            Don't colorize the command output.
      --version             show program's version number and exit
      -h, --help            show this help message and exit
