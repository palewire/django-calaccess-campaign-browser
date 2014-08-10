Django Cal-Access browser
=========================

**django-calacces-browser** is a simple Django app to build campaign
finance data from the cal access database. It is reliant on
`django-calaccess-parser <https://github.com/california-civic-data-coalition/django-calaccess-parser>`__.

Detailed documentation is in the "docs" directory. *(coming soon)*

Requirements
------------

-  Django 1.6
-  `django.contrib.humanize <https://docs.djangoproject.com/en/1.6/ref/contrib/humanize/>`__
-  MySQL 5.5
-  `django-calaccess-parser <https://github.com/california-civic-data-coalition/django-calaccess-parser>`__
-  Patience

Installation
------------

-  Install django-calaccess-browser with pip

   .. code:: bash

       $ pip install https://github.com/california-civic-data-coalition/django-calaccess-browser/archive/master.zip

-  Add ``campaign_finance`` to your INSTALLED\_APPS setting like this:

   .. code:: python

       INSTALLED_APPS = (
           ...
           'campaign_finance',
       )

   Setup urls
   ----------

   In your project ``urls.py``:

   .. code:: python

       ...
       urlpatterns = patterns('',
           url(r'^browser/', include('campaign_finance.urls')),    
       )

   Loading the data
   ----------------

-  Next, sync the database, create a Django admin user, and run the
   management command to extract campaign finance data from from the raw
   calaccess data dump.

   .. code:: bash

       $ python manage.py syncdb
       $ python manage.py build_campaign_finance

   :warning: This'll take a while. Go grab some coffee or do something
   else productive with your life.

Building
--------

The JavaScript and CSS for the project is managed with Grunt and Bower.
Currently, the JavaScript and SCSS dependencies are not included so
you'll need to build them yourself;

1. Install `Node.js <http://nodejs.org/>`__ (this will also include NPM)
2. Install Grunt and bower globally with
   ``npm install -g bower grunt-cli``
3. Go to the ``static`` directory and install the required dependencies
   with ``npm install && bower install``
4. Generate the ``main.css`` file and watch for HTML, CSS and JavaScript
   changes by executing ``grunt``

Explore data
------------

Start the development server and visit http://127.0.0.1:8000/browser/ to
inspect the Cal-access data.

API
---

django-calaccess-browser uses django-tastypie to expose the data as an
API. Add ``tastypie`` to the project ``INSTALLED_APPS`` and make sure
you included ``campaign_finance.urls`` in your project's ``urls.py``.

From there visit
`127.0.0.1:8000/browser/api/v1/filer/?format=json <127.0.0.1:8000/browser/api/v1/filer/?format=json>`__
to explore the JSON representation of the data.

Export
------

You can also export the data into easily queryable flat files.

.. code:: bash

    $ python manage.py export_campaign_finance

Update the data
---------------

When you are ready to get new data, just blow away both the parser and
the campaign finance browser app. Then reload them.

You can do something like this, making sure you fill in your database
and user names correctly.
``bash  $ python manage.py sqlclear calaccess | mysql -u user_name -p database_name  $ python manage.py sqlclear campaign_finance | mysql -u user_name -p database_name  $ pytnon manage.py syncdb  $ python manage.py downloadcalaccess && python manage.py build_campaign_finance``

Authors
-------

-  `Agustin Armendariz <https://github.com/armendariz>`__
-  `Ben Welsh <https://github.com/palewire>`__
-  `Aaron Williams <https://github.com/aboutaaron>`__

