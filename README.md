# Django Cal-Access browser

**django-calacces-browser** is a simple Django app to build campaign finance data from the cal access database. It is reliant on [django-calaccess-parser](https://github.com/california-civic-data-coalition/django-calaccess-parser).

Detailed documentation is in the "docs" directory. *(coming soon)*

## Requirements
- Django 1.6
- MySQL 5.5
- [django-calaccess-parser](https://github.com/california-civic-data-coalition/django-calaccess-parser)
- Patience

## Installation
- Install django-calaccess-browser with pip
```bash
$ pip install https://github.com/california-civic-data-coalition/django-calaccess-browser/archive/0.1-alpha.1.tar.gz
```

- Add `campaign_finance` to your INSTALLED_APPS setting like this:
```python
INSTALLED_APPS = (
    ...
    'campaign_finance',
)
```
## Setup urls
In your project `urls.py`:
```python
...
urlpatterns = patterns('',
    url(r'^browser/', include('campaign_finance.urls')),    
)
```
## Loading the data
- Next, sync the database, create a Django admin user, and run the management command to extract campaign finance data from from the raw calaccess data dump.
```bash
$ python manage.py syncdb
$ python manage.py build_campaign_finance
```
:warning: This'll take a while. Go grab some coffee or do something else productive with your life.


## Explore data
Start the development server and visit [http://127.0.0.1:8000/browser/](http://127.0.0.1:8000/browser/)
   to inspect the Cal-access data.

## Authors
- [Agustin Armendariz](https://github.com/armendariz)
- [Ben Welsh](https://github.com/palewire)
- [Aaron Williams](https://github.com/aboutaaron)
