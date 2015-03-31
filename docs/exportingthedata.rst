Exporting the data
==================

This walkthrough will show you how to export the database tables for the ``Contribution`` and ``Expenditure`` models as CSV files.

This assumes that you have installed the project and ran the ``buildcalaccesscampaignbrowser`` command.

.. code-block:: bash

    $ python manage.py buildcalaccesscampaignbrowser

From here, you can now run the export command to get a dump of the data from the database.

.. code-block:: bash

    $ python manage.py exportcalaccesscampaignbrowser


This will export the CSVs as ``YYYY-MM-DD-model.csv`` to ``os.path.join(settings.BASE_DIR, 'data')``
