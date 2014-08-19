import gc
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import reset_queries

try:
    from calaccess_raw.models import (
        RcptCd,
    )

except:
    print 'you need to load the raw calaccess data app'

from calaccess_campaign_browser.models import (
    Contribution,
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
    help = 'Isolate recipient committee campaign finance data'

    def handle(self, *args, **options):
        call_command("loadcalaccesscampaignfilers")
        call_command("loadcalaccesscampaignfilings")
        call_command("loadcalaccesscampaignsummary")
        self.load_contributions()
        call_command("loadcalaccesscampaignexpends")

    def load_contributions(self):
        insert_stats = {}
        insert_obj_list = []
        for f in queryset_iterator(Filing.objects.all()):
            qs = RcptCd.objects.filter(
                filing_id=f.filing_id_raw, amend_id=f.amend_id)
            filing_key = '%s-%s' % (f.filing_id_raw, f.amend_id)
            insert_stats[filing_key] = qs.count()
            if qs.count() > 0:
                for q in queryset_iterator(qs):

                    if q.ctrib_namf == '':
                        raw_org_name = q.ctrib_naml
                        person_flag = False
                    else:
                        raw_org_name = q.ctrib_emp
                        person_flag = True

                    insert = Contribution()
                    insert.cycle = f.cycle
                    insert.committee = f.committee
                    insert.filing = f
                    insert.dupe = f.dupe
                    insert.ctrib_namt = q.ctrib_namt
                    insert.ctrib_occ = q.ctrib_occ
                    insert.ctrib_nams = q.ctrib_nams
                    insert.line_item = q.line_item
                    insert.amend_id = q.amend_id
                    insert.rec_type = q.rec_type
                    insert.ctrib_namf = q.ctrib_namf
                    insert.date_thru = q.date_thru
                    insert.ctrib_naml = q.ctrib_naml
                    insert.ctrib_self = q.ctrib_self
                    if q.rcpt_date:
                        insert.rcpt_date = q.rcpt_date
                    insert.ctrib_zip4 = q.ctrib_zip4
                    insert.ctrib_st = q.ctrib_st
                    insert.ctrib_adr1 = q.ctrib_adr1
                    insert.ctrib_adr2 = q.ctrib_adr2
                    insert.memo_refno = q.memo_refno
                    insert.intr_st = q.intr_st
                    insert.memo_code = q.memo_code
                    insert.intr_self = q.intr_self
                    insert.intr_occ = q.intr_occ
                    insert.intr_emp = q.intr_emp
                    insert.entity_cd = q.entity_cd
                    insert.intr_cmteid = q.intr_cmteid
                    insert.ctrib_city = q.ctrib_city
                    insert.bakref_tid = q.bakref_tid
                    insert.tran_type = q.tran_type
                    insert.intr_adr2 = q.intr_adr2
                    insert.cum_ytd = q.cum_ytd
                    insert.intr_adr1 = q.intr_adr1
                    insert.form_type = q.form_type
                    insert.intr_city = q.intr_city
                    insert.cmte_id = q.cmte_id
                    insert.xref_schnm = q.xref_schnm
                    insert.ctrib_emp = q.ctrib_emp
                    insert.xref_match = q.xref_match
                    insert.cum_oth = q.cum_oth
                    insert.ctrib_dscr = q.ctrib_dscr
                    insert.intr_namt = q.intr_namt
                    insert.intr_nams = q.intr_nams
                    insert.amount = q.amount
                    insert.intr_naml = q.intr_naml
                    insert.intr_zip4 = q.intr_zip4
                    insert.intr_namf = q.intr_namf
                    insert.tran_id = q.tran_id
                    insert.raw_org_name = raw_org_name
                    insert.person_flag = person_flag

                    insert_obj_list.append(insert)
                    if len(insert_obj_list) == 5000:
                        Contribution.objects.bulk_create(insert_obj_list)
                        insert_obj_list = []

                        reset_queries()
                        gc.collect()

        if len(insert_obj_list) > 0:
            Contribution.objects.bulk_create(insert_obj_list)
            insert_obj_list = []

        cnt = Contribution.objects.count()

        if sum(insert_stats.values()) == cnt:
            print 'loaded %s contributions' % cnt

        else:
            print (
                'loaded {0} contributions but {1} records queried'
                .format(cnt, sum(insert_stats.values()))
            )

        insert_stats = {}

        reset_queries()
        gc.collect()
