#!/usr/bin/env python
import csv
from django.db.models.loading import get_model

import gc

def queryset_iterator(queryset, chunksize=1000):
    '''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    
    https://djangosnippets.org/snippets/1949/
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()

def dump_csv(qs, outfile_path):
        """
        Palewire recipe: http://palewi.re/posts/2009/03/03/django-recipe-dump-your-queryset-out-as-a-csv-file/
        Takes in a Django queryset and spits out a CSV file.
        
        Usage::
        
                >> from utils import dump2csv
                >> from dummy_app.models import *
                >> qs = DummyModel.objects.all()
                >> dump2csv.dump(qs, './data/dump.csv')
        
        Based on a snippet by zbyte64::
                
                http://www.djangosnippets.org/snippets/790/
        
        """
        model = qs.model
        writer = csv.writer(open(outfile_path, 'w'))
        
        headers = []
        for field in model._meta.fields:
                headers.append(field.name)
        writer.writerow(headers)
        
        for obj in queryset_iterator(qs):
                row = []
                for field in headers:
                        val = getattr(obj, field)
                        if callable(val):
                                val = val()
                        if type(val) == unicode:
                                val = val.encode("utf-8")
                        row.append(val)
                writer.writerow(row)
