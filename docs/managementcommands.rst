Management commands
===================

build_campaign_finance
------------------

.. code-block:: bash

    Usage: manage.py build_campaign_finance [options]

    Break out the recipient committee campaign finance data from the CAL-ACCESS dump

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
      --version             show program's version number and exit
      -h, --help            show this help message and exit


export_campaign_finance
---------------------
.. code-block:: bash

    Usage: manage.py export_campaign_finance [options]

    Export parsed data as csv files. Mashes the relational tables down to three easy to query tables.

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
      --skip-contributions  Skip contributions export
      --skip-expenditures   Skip expenditures export
      --skip-summary        Skip summary export
      --version             show program's version number and exit
      -h, --help            show this help message and exit
