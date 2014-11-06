How to use it
=============

This library is intended to be plugged into project created with the Django web
framework. Before you can begin, you'll need to get one of those up and running.
If you don't know how, go `check out the official Django documentation <https://docs.djangoproject.com/en/dev/intro/tutorial01/>`_. 


Once you've got that going, install this application and its dependencies with ``pip``.

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

Make sure you have MySQL installed. If you don't, now is the time to hit Google and figure out how. If
you're using Apple's OSX operating system, you can `install via 
Homebrew <http://benjsicam.me/blog/how-to-install-mysql-on-mac-os-x-using-homebrew-tutorial/>`_.
Then create a new database named ``calaccess``.

.. code-block:: bash

    $ mysqladmin -h localhost -u root -p create calaccess

Also in the Django settings, configure a database connection. Currently this application only supports MySQL backends.

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'calaccess',
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

    $ python manage.py migrate

Run the management command that installs the raw data dump from the California Secretary of State.

.. code-block:: bash

    $ python manage.py downloadcalaccessrawdata

Run the management command that extracts and refines campaign finance data from from the raw CAL-ACCESS data dump.

.. code-block:: bash

   $ python manage.py buildcalaccesscampaignbrowser

In your project ``urls.py`` file, add this app's URLs:

.. code-block:: python

   urlpatterns = patterns('',
       url(r'^browser/', include('calaccess_campaign_browser.urls')),
   )

Start the development server and visit ``http://127.0.0.1:8000/browser/`` to
inspect the data.

.. code-block:: bash

    $ python manage.py runserver
