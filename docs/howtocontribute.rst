How to contribute
=================

This walkthrough will show you how to install the source code of this application
to fix bugs and develop new features.

First create a new virtualenv.

.. code-block:: bash

    $ virtualenv django-calaccess-campaign-finance

Jump in.

.. code-block:: bash

    $ cd django-calaccess-campaign-finance
    $ . bin/activate

Clone the repository from `GitHub <https://github.com/california-civic-data-coalition/django-calaccess-campaign-finance>`_.

Make sure you have the `django-calaccess-parser <https://github.com/california-civic-data-coalition/django-calaccess-campaign-parser>`_ installed otherwise NONE OF THIS WILL WORK.

.. code-block:: bash

    $ git clone https://github.com/california-civic-data-coalition/django-calaccess-campaign-finance.git repo

Move into it and install the Python dependencies.

.. code-block:: bash

    $ cd repo
    $ pip install -r requirements_dev.txt

Make sure you have MySQL installed. If you don't, now is the time to hit Google and figure out how. If
you're using Apple's OSX operating system, you can `install via Homebrew <http://benjsicam.me/blog/how-to-install-mysql-on-mac-os-x-using-homebrew-tutorial/>`_. If you need to clean up after a previous MySQL installation, `this might help <http://stackoverflow.com/questions/4359131/brew-install-mysql-on-mac-os/6378429#6378429>`_.

Then create a new database named ``campaign_finance``.

.. code-block:: bash

    mysqladmin -h localhost -u root -p create campaign_finance

If you have a different username, substitute it above. You'll be prompted for that user's mysql password.

Then create a file at ``example/project/settings_local.py`` to save your custom database credentials. That
might look something like this.

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'campaign_finance',
            'USER': 'yourusername', # <-- This
            'PASSWORD': 'yourpassword', # <-- And this
            'HOST': 'localhost',
            'PORT': '3306',
            'OPTIONS': {
                'local_infile': 1,
            }
        }
    }

Finally create your database and get to work.

.. code-block:: bash

    $ python example/manage.py syncdb

You might start by loading the data dump from the web.

.. code-block:: bash

    $ python example/manage.py downloadcalaccess

Then you can build the campaign finance models

.. code-block:: bash

    $ python example/manage.py build_campaign_finance

Finally, you could export the data into CSVs for reporters to dig into

.. code-block:: bash

    $ python example/manage.py export_campaign_finance
