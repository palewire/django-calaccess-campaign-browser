How to use it
=============

Install the application and its dependencies with ``pip``

.. code-block:: bash

   $ pip install django-calaccess-campaign-finance

Add this ``campaign_finance`` app as well as the underlying ``calaccess`` app
that contains the raw government database it will work with to refine to your Django project's ``settings.py`` file:

.. code-block:: python

   INSTALLED_APPS = (
       ...
       'calaccess',
       'campaign_finance',
   )

In your project ``urls.py`` file, add this app's URLs:

.. code-block:: python

   urlpatterns = patterns('',
       url(r'^browser/', include('campaign_finance.urls')),
   )

Next, sync the database and create a Django admin user.

.. code-block:: bash

   $ python manage.py syncdb

Run the management command that installs the raw data dump from the California
Secretary of State.

.. code-block:: bash

    $ python manage.py downloadcalaccess

Run the management command that extracts and refines campaign finance data from from the raw
calaccess data dump.

.. code-block:: bash

   $ python manage.py build_campaign_finance

Start the development server and visit ``http://127.0.0.1:8000/browser/`` to
inspect the data.

.. code-block:: bash

    $ python manage.py runserver
