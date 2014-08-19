import gc
from django.db import reset_queries
from calaccess_raw.models import SmryCd
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.models import Filing, Summary


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

    def handle(self):
        '''
        Currently using a dictonary to parse the summary
        information by form type, schedule and line number.
        '''
        summary_form_dict = {
            'F460': {
                # 'name': 'Recipient Committee Campaign Statement',
                'itemized_monetary_contribs': {'sked': 'A', 'line_item': 1},
                'unitemized_monetary_contribs': {'sked': 'A', 'line_item': 2},
                'total_monetary_contribs': {'sked': 'A', 'line_item': 3},
                'non_monetary_contribs': {'sked': 'F460', 'line_item': 4},
                'total_contribs': {'sked': 'F460', 'line_item': 5},
                'itemized_expenditures': {'sked': 'E', 'line_item': 1},
                'unitemized_expenditures': {'sked': 'E', 'line_item': 2},
                'total_expenditures': {'sked': 'E', 'line_item': 4},
                'ending_cash_balance': {'sked': 'F460', 'line_item': 16},
                'outstanding_debts': {'sked': 'F460', 'line_item': 19},
            },
            'F450': {
                # 'Recipient Committee Campaign Statement -- Short Form'
                # 'name': "" -- Short Form',
                'itemized_monetary_contribs': None,
                'unitemized_monetary_contribs': None,
                'total_monetary_contribs': {'sked': 'F450', 'line_item': 7},
                'non_monetary_contribs': {'sked': 'F450', 'line_item': 8},
                'total_contribs': {'sked': '450', 'line_item': 10},
                'itemized_expenditures': {'sked': 'F450', 'line_item': 1},
                'unitemized_expenditures': {'sked': 'F450', 'line_item': 2},
                'total_expenditures': {'sked': 'E', 'line_item': 6},
                'ending_cash_balance': {'sked': 'F460', 'line_item': 15},
                'outstanding_debts': None,
            }
        }
        insert_stats = {}
        i = 0
        bulk_recrods = []
        for f in queryset_iterator(Filing.objects.all()):
            qs = SmryCd.objects.filter(
                filing_id=f.filing_id_raw, amend_id=f.amend_id)
            f_id = '%s-%s' % (f.filing_id_raw, f.amend_id)
            insert_stats[f_id] = qs.count()

            if qs.count() > 0:
                query_dict = summary_form_dict[f.form_id]
                insert = Summary()
                insert.committee = f.committee
                insert.cycle = f.cycle
                insert.form_type = f.form_id
                insert.filing = f
                insert.dupe = f.dupe
                for k, v in query_dict.items():
                    try:
                        insert.__dict__[k] = qs.get(
                            form_type=v['sked'],
                            line_item=v['line_item']
                        ).amount_a

                    except:
                        insert.__dict__[k] = 0
                i += 1
                bulk_recrods.append(insert)
                if i % 5000 == 0:
                    Summary.objects.bulk_create(bulk_recrods)
                    bulk_recrods = []
                    print '%s records created ...' % i
                    reset_queries()
                    gc.collect()

        if len(bulk_recrods) > 0:
            Summary.objects.bulk_create(bulk_recrods)
            bulk_recrods = []
            print '%s records created ...' % i

        print 'loaded summary'

        filings_no_data_cnt = 0
        filings_with_data_cnt = 0
        for v in insert_stats.values():
            if v == 0:
                filings_no_data_cnt += 1
            elif v > 0:
                filings_with_data_cnt += 1

        total_filing_cnt = Filing.objects.count()
        pct_filings_have_data = (
            filings_with_data_cnt / float(total_filing_cnt)) * 100

        print (
            '{0} total filings processed, {1} percent have data'
            .format(total_filing_cnt, pct_filings_have_data)
        )

        if Summary.objects.count() == filings_with_data_cnt:
            print 'All filings with data represented in Summary table'

        reset_queries()
        gc.collect()
