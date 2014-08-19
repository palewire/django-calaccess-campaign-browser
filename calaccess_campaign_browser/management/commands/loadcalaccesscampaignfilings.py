import gc
from django.core.management.base import BaseCommand
from django.db import reset_queries
from django.db.models import Q

try:
    from calaccess_raw.models import (
        FilerFilingsCd,
        SmryCd
    )

except:
    print 'you need to load the raw calaccess data app'

from calaccess_campaign_browser.models import (
    Committee,
    Cycle,
    Filing,
)


def queryset_iterator(queryset, chunksize=1000):
    '''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator
    does not support ordered query sets.

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

class Command(BaseCommand):

    def handle(self, *args, **options):
        '''
        Loads all filings, using the most current, amended filing
        '''
        insert_obj_list = []

        for c in queryset_iterator(Committee.objects.all()):
            qs_filings = FilerFilingsCd.objects.filter(
                Q(form_id='F460') | Q(form_id='F450'), filer_id=c.filer_id_raw)

            filing_ids = (
                qs_filings
                .values_list('filing_id', flat=True)
                .distinct()
            )

            for f_id in filing_ids:

                current_filing = qs_filings.filter(
                    filing_id=f_id).order_by('-filing_sequence')[0]

                summary_count = (
                    SmryCd
                    .objects
                    .filter(filing_id=current_filing.filing_id)
                    .count()
                )

                if summary_count > 0:
                    insert = Filing()
                    if current_filing.session_id % 2 == 0:
                        cycle_year = current_filing.session_id
                    else:
                        cycle_year = current_filing.session_id + 1
                    insert.cycle, created = Cycle.objects.get_or_create(
                        name=cycle_year)
                    insert.committee = c
                    insert.filing_id_raw = current_filing.filing_id
                    insert.amend_id = current_filing.filing_sequence
                    insert.form_id = current_filing.form_id

                    if current_filing.rpt_start:
                        insert.start_date = (
                            current_filing
                            .rpt_start
                            .isoformat()
                        )

                    if current_filing.rpt_end:
                        insert.end_date = (
                            current_filing
                            .rpt_end
                            .isoformat()
                        )

                    insert_obj_list.append(insert)

                    if len(insert_obj_list) == 5000:
                        Filing.objects.bulk_create(insert_obj_list)
                        insert_obj_list = []

        if len(insert_obj_list) > 0:
            Filing.objects.bulk_create(insert_obj_list)
            insert_obj_list = []

        print 'loaded filings'
        gc.collect()
        reset_queries()

        # get dupe filings flagged
        d = {}
        for f in Filing.objects.all():
            id_num = f.filing_id_raw
            if id_num not in d:
                d[id_num] = 1
            else:
                d[id_num] += 1

        filing_id_list = []
        for k, v in d.items():
            if v > 1:
                filing_id_list.append(k)
                # print '%s\t%s' % (k,v)

        for id_num in filing_id_list:
            qs = Filing.objects.filter(filing_id_raw=id_num).order_by('-id')
            keeper = qs[0]
            for q in qs.exclude(id=keeper.id):
                q.dupe = True
                q.save()

        print 'flagged dupe filings'
        gc.collect()
        reset_queries()
