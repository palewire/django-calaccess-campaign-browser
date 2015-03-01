How to contribute
=================

This walkthrough will show you how to install the source code of this application
to fix bugs and develop new features.

First create a new virtualenv.

.. code-block:: bash

    $ virtualenv django-calaccess-campaign-browser

Jump in.

.. code-block:: bash

    $ cd django-calaccess-campaign-browser
    $ . bin/activate

Clone the repository from `GitHub <https://github.com/california-civic-data-coalition/django-calaccess-campaign-browser>`_.

.. code-block:: bash

    $ git clone https://github.com/california-civic-data-coalition/django-calaccess-campaign-browser.git repo

.. warning::

    At this point you need a make a choice. Do you want to install a copy of the database on your computer, or do you want to offload that work to the cloud? If you've never installed MySQL before, you might want to let the cloud handle this one for you.

Relying on a cloud database
---------------------------

Move into the repository and install only enough Python dependencies to use the cloud database.

.. code-block:: bash

    $ cd repo
    $ pip install -r requirements_cloudmysql.txt

Create a file to store your custom database credentials.

.. code-block:: bash

    $ touch example/project/settings_local.py

Open that file and add the following configuration, which will connect to a cloud-hosted database we’ve prepared.

.. code-block:: bash

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'ccdc',
            'USER': 'ccdc',
            'PASSWORD': 'ccdcccdc',
            'HOST': '<HOST NAMES GOES HERE>',
            'PORT': '3306',
        }
    }

Do this one bit of arcane Django housekeeping.

.. code-block:: bash

    $ python example/manage.py collectstatic  --noinput

Activate Django’s web server and visit `http://localhost:8000 <http://localhost:8000>`_ in your web browser.

.. code-block:: bash

    $ python example/manage.py runserver

Installing a copy of the database to your computer
--------------------------------------------------

Move into the repository and install the Python dependencies.

.. code-block:: bash

    $ cd repo
    $ pip install -r requirements_dev.txt

Make sure you have MySQL installed. If you don't, now is the time to hit Google and figure out how. If
you're using Apple's OSX operating system, you can `install via Homebrew <http://benjsicam.me/blog/how-to-install-mysql-on-mac-os-x-using-homebrew-tutorial/>`_. If you need to clean up after a previous MySQL installation, `this might help <http://stackoverflow.com/questions/4359131/brew-install-mysql-on-mac-os/6378429#6378429>`_.

Then create a new database named ``calaccess``.

.. code-block:: bash

    mysqladmin -h localhost -u root -p create calaccess

If you have a different username, substitute it above. You'll be prompted for that user's mysql password.

Then create a file at ``example/project/settings_local.py`` to save your custom database credentials. That
might look something like this.

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'calaccess',
            'USER': 'yourusername',
            'PASSWORD': 'yourpassword',
            'HOST': 'localhost',
            'PORT': '3306',
            'OPTIONS': {
                'local_infile': 1,
            }
        }
    }

Finally create your database and get to work.

.. code-block:: bash

    $ python example/manage.py migrate

You might start by loading the data dump from the web.

.. code-block:: bash

    $ python example/manage.py downloadcalaccessrawdata

Then you can build the campaign finance models

.. code-block:: bash

    $ python example/manage.py buildcalaccesscampaignbrowser

And fire up the Django test server to use the browser

.. code-block:: bash

    $ python example/manage.py collectstatic
    $ python example/manage.py runserver
