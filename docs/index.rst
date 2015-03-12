django-calaccess-campaign-browser
=================================

A Django app to refine and investigate campaign finance data drawn from the
California Secretary of State's `CAL-ACCESS <http://cal-access.ss.ca.gov/default.aspx>`_ database.

Intended as a second layer atop `django-calaccess-raw-data <https://github.com/california-civic-data-coalition/django-calaccess-raw-data>`_
that transforms the source data and loads it into simplified models that serve as a platform
for investigative analysis.

.. image:: /_static/application-layers.png

.. warning::

    This is a work in progress. Its analysis should be considered as provisional
    until it is further tested and debugged.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   howtouseit
   managementcommands
   models
   howtocontribute
   changelog

Open-source resources
---------------------

* Code: `github.com/california-civic-data-coalition/django-calaccess-campaign-browser <https://github.com/california-civic-data-coalition/django-calaccess-campaign-browser>`_
* Issues: `github.com/california-civic-data-coalition/django-calaccess-campaign-browser/issues <https://github.com/california-civic-data-coalition/django-calaccess-campaign-browser/issues>`_
* Packaging: `pypi.python.org/pypi/django-calaccess-campaign-browser <https://pypi.python.org/pypi/django-calaccess-campaign-browser>`_
* Testing: `travis-ci.org/california-civic-data-coalition/django-calaccess-campaign-browser <https://travis-ci.org/california-civic-data-coalition/django-calaccess-campaign-browser>`_
* Coverage: `coveralls.io/r/california-civic-data-coalition/django-calaccess-campaign-browser <https://coveralls.io/r/california-civic-data-coalition/django-calaccess-campaign-browser>`_

Read more
---------

* `'CAL-ACCESS Dreaming' <https://docs.google.com/presentation/d/1YfdiZdSIDk_Jys5yBBRdddYtE-LXbwVoAPbb0ysmuCc/pub?start=false&loop=false&delayms=3000>`_, the kickoff presentation from the initial code convening (Aug. 13, 2014)
* `'Introducing the California Civic Data Coalition' <http://www.californiacivicdata.org/2014/09/24/hello-world/>`_, a blog post annoucing the first public code release (Sept. 24, 2014)
* `'Package data like software, and the stories will flow like wine' <http://www.californiacivicdata.org/2014/09/24/pluggable-data/>`_, a polemic explaining this project's software design philosophy (Sept. 24, 2014)
* `'Light everywhere: The California Civic Data Coalition wants to make public datasets easier to crunch' <http://www.niemanlab.org/2014/10/light-everywhere-the-california-civic-data-coalition-wants-to-make-public-datasets-easier-to-crunch/>`_, a story about the creators by Nieman Journalism Lab (Oct. 20, 2014)
* `'Once a crusader against big money, Gov. Brown is collecting millions' <http://www.latimes.com/local/politics/la-me-pol-brown-money-20141031-story.html#page=1>`_, a Los Angeles Times story that utilized this application (Oct. 31, 2014)

Events
------

Development has been advanced by a series of sprints supported by `Knight-Mozilla OpenNews <http://opennews.org/>`_.

* August 13-15, 2014, at `Mozilla's offices in San Francisco <https://www.mozilla.org/en-US/contact/spaces/san-francisco/>`_
* January 14-15, 2015, at `USC's Wallis Annenberg Hall <http://wallisannenberghall.uscannenberg.org/>`_
* March 4-8, 2015, the California Code Rush at `NICAR 2015 in Atlanta <http://www.californiacivicdata.org/2015/03/11/code-rush-recap/>`_

Sponsors
--------

.. image:: /_static/ccdc-logo.png
   :height: 70px
   :target: http://www.californiacivicdata.org/

.. image:: /_static/los-angeles-times-logo.png
   :height: 70px
   :target: http://www.github.com/datadesk/

.. image:: /_static/cir-logo.png
   :height: 70px
   :target: http://cironline.org/

.. image:: /_static/stanford-logo.png
   :height: 70px
   :target: http://journalism.stanford.edu/

.. image:: /_static/opennews-logo.png
   :height: 80px
   :target: http://opennews.org/code.html
