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

Also in the Django settings, configure a database connection. Currently this application only supports MySQL backends.

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'my_calaccess_db',
            'USER': 'username',
            'PASSWORD': 'password',
            'HOST': 'localhost',
            'PORT': '3306',
            # You'll need this to use our data loading tricks
            'OPTIONS': {
                'local_infile': 1,
            }
        }
    }

Now you're ready to sync the database tables.

.. code-block:: bash

    $ python manage.py syncdb

A final setting, ``CALACCESS_DOWNLOAD_DIR``, tels our application where to store the large files it's going to download. You can put it anywhere you want.

.. code-block:: python

    CALACCESS_DOWNLOAD_DIR = "/path/to/wherever/"

Or you could put the files in your system's temp directory, if you felt like it

.. code-block:: python

    import tempfile
    CALACCESS_DOWNLOAD_DIR = tempfile.gettempdir()

Run the management command that installs the raw data dump from the California
Secretary of State.

.. code-block:: bash

    $ python manage.py downloadcalaccess

Run the management command that extracts and refines campaign finance data from from the raw
calaccess data dump.

.. code-block:: bash

   $ python manage.py build_campaign_finance

In your project ``urls.py`` file, add this app's URLs:

.. code-block:: python

   urlpatterns = patterns('',
       url(r'^browser/', include('campaign_finance.urls')),
   )

Start the development server and visit ``http://127.0.0.1:8000/browser/`` to
inspect the data.

.. code-block:: bash

    $ python manage.py runserver
