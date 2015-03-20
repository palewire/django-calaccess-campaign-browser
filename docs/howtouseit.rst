How to use it
=============

This guide will walk users through the process of installing the latest official release `from the Python Package Index <https://pypi.python.org/pypi/django-calaccess-campaign-browser/>`_. If you want to install the raw source code or contribute as a developer refer to the `"How to contribute" <howtocontribute.html>`__ page.

.. warning::

    This library is intended to be plugged into a project created with the Django web framework. Before you can begin, you'll need to have one up and running. If you don't know how, `check out the official Django documentation <https://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

Installing the Django app
-------------------------

The latest official release of the application can be installed from the Python Package Index using ``pip``.

.. code-block:: bash

   $ pip install django-calaccess-campaign-browser

Add this ``calaccess_campaign_browser`` app as well as the underlying ``calaccess_raw`` app
that contains the raw government database to your Django project's ``settings.py`` file.

.. code-block:: python

   INSTALLED_APPS = (
       ...
       'calaccess_raw',
       'calaccess_campaign_browser',
   )

Connecting to a local database
------------------------------

Also in the ``settings.py`` file, you will need to configure Django so it can connect to a database.

Unlike a typical Django project, this application only supports the MySQL database backend. This is because we enlist specialized tools to load the immense amount of source data more quickly than Django typically allows. We haven't worked out those routines for PostgreSQL, SQLite and the other Django backends yet, but we're working on it.

Preparing MySQL
~~~~~~~~~~~~~~~

Before you begin, make sure you have a MySQL server installed. If you don't, now is the time to hit Google and figure out how. If you're using Apple's OSX operating system, you can `install via Homebrew <http://thisdotlife.com/2013/05/30/how-to-install-mysql-on-mac-os-x-using-homebrew-tutorial/>`_. `Here <http://dev.mysql.com/doc/refman/5.5/en/installing.html>`_ is the official MySQL documentation for how to get it done.

Once that is handled, create a new database named ``calaccess``.

.. code-block:: bash

    $ mysqladmin -h localhost -u your-username-here -p create calaccess

Also in the Django ``settings.py``, configure a database connection.

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'calaccess',
            'USER': 'your-username-here',
            'PASSWORD': 'your-password-here',
            'HOST': 'localhost',
            'PORT': '3306',
            # You'll need this to use our data loading tricks
            'OPTIONS': {
                'local_infile': 1,
            }
        }
    }

Loading the data
----------------

Now you're ready to create the database tables with Django using its ``manage.py`` utility belt.

.. code-block:: bash

    $ python manage.py migrate

Once everything is set up, this management command will download the latest bulk data release from the state and load it in the database. It'll take a while. Go grab some coffee.

.. code-block:: bash

    $ python manage.py downloadcalaccessrawdata

Next, run the management command that extracts and refines campaign finance data from from the raw CAL-ACCESS data dump.

.. code-block:: bash

   $ python manage.py buildcalaccesscampaignbrowser

Exploring the data
------------------

In your project ``urls.py`` file, add this app's URLs:

.. code-block:: python

   urlpatterns = patterns('',
       url(r'^', include('calaccess_campaign_browser.urls')),
   )

Finally start the development server and visit `localhost:8000 <http://localhost:8000/>`_ in your browser to start using the app.

.. code-block:: bash

    $ python manage.py runserver
