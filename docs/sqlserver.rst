Importing to Microsoft SQL Server
===============================

This walkthough will show you how to import the exported CSV data to `Microsoft SQL Server <http://www.microsoft.com/en-us/server-cloud/products/sql-server/>`_. This guide assumes you already have SQL server installed and running.

First build the browser and export the tables:

.. code-block:: bash

    $ python manage.py buildcalaccesscampaignbrowser
    $ python manage.py exportcalaccesscampaignbrowser

Setting up pypyodbc
-------------------
In order to connect to SQL Server from the application, we'll need to install `pypyodbc <https://github.com/jiangwen365/pypyodbc>`_, an `open database connectivity` library that allows Python to communicate with multiple databases.

Installation is simple:

.. code-block:: bash

    $ pip install pypyodbc

---------------------------
Configure ODBC and Free TDS
---------------------------
You'll need to install ODBC and configure its database drivers.

**Mac OS X** users can install ODBC and Free TDS with homebrew:

**`Note:` This has not been tested and should be considered provisional**

.. code-block:: bash

    $ brew install unixodbc
    $ brew install freetds

**Linux** users can follow these instructions are from `the project wiki <https://code.google.com/p/pypyodbc/wiki/Linux_ODBC_in_3_steps>`_:

1. Install ODBC and Free TDS

.. code-block:: bash

    $ sudo apt-get install tdsodbc unixodbc

2. Modify ``/etc/odbcinst.ini``

**From the wiki**: "If ``odbcinst.ini`` doesn't exist under /etc, create the file. Find the path to ``libtdsodbc.so``. If the path to the file is ``/usr/lib/x86_64-linux-gnu/libtdsodbc.so``, make sure you have the below content in the file:"

.. code-block:: bash

    [FreeTDS]
    Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so

3. Modify /etc/freetds/freetds.conf

**From the wiki**: "Make sure there are following lines under the "Global" section in the file:"

.. code-block:: bash

    [Global]
    TDS_Version = 8.0
    client charset = UTF-8


Connecting to the server
------------------------

Next, you'll need to add the SQL server variables to your ``settings.py``. Since this will contain sensitive information, we suggest storing these variables in a ``local_settings.py`` file that's not tracked by version control and importing it.

.. code-block:: python

    SQL_SERVER_DRIVER = ''  # Use 'FreeTDS' if you followed instructions above
    SQL_SERVER_ADDRESS = ''  # Your SQL Server IP address
    SQL_SERVER_PORT = ''  # Your SQL Server port number
    SQL_SERVER_USER = ''  # Your SQL server username
    SQL_SERVER_PASSWORD = ''  # Your SQL server password
    SQL_SERVER_DATABASE = '' # Your SQL server database name


Import data into SQL Server
---------------------------

With the above configuration, you should now be able to import the exported CSV data from your local folder to SQL server:

.. code-block:: bash

    $ python manage.py importtosqlserver
