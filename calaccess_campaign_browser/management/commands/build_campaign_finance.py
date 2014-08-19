import gc
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import reset_queries

try:
    from calaccess_raw.models import (
        ExpnCd, RcptCd,
        SmryCd
    )

except:
    print 'you need to load the raw calaccess data app'

from calaccess_campaign_browser.models import (
    Committee,
    Contribution,
    Expenditure,
    Filing,
    Summary
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


def insert_cmte(filer_obj, cmte_filer_id_raw, cmte_type,
                cmte_name, cmte_xref_id, effective_date):

    insert_cmtee = Committee()
    # tie all candidate committees to the CAL-ACCESS candidate filer
    insert_cmtee.filer = filer_obj
    # preserve the CAL-ACCESS filer_id for the committee here, but don't add
    # it to our Filer model. So can distinguish PAC from Cand Cmtee
    insert_cmtee.filer_id_raw = cmte_filer_id_raw
    insert_cmtee.committee_type = cmte_type
    insert_cmtee.name = cmte_name
    insert_cmtee.xref_filer_id = cmte_xref_id
    insert_cmtee.save()


class Command(BaseCommand):
    help = 'Isolate recipient committee campaign finance data'

    def handle(self, *args, **options):
        call_command("loadcalaccesscampaignfilers")
        call_command("loadcalaccesscampaignfilings")
        self.load_summary()
        self.load_contributions()
        self.load_expenditures()

    def load_summary(self):
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

    def load_expenditures(self):
        '''
        All campaign expenditures
        '''
        insert_stats = {}
        insert_obj_list = []
        for f in queryset_iterator(Filing.objects.all()):
            qs = ExpnCd.objects.filter(
                filing_id=f.filing_id_raw, amend_id=f.amend_id)
            filing_key = '%s-%s' % (f.filing_id_raw, f.amend_id)
            insert_stats[filing_key] = qs.count()
            if qs.count() > 0:
                for q in queryset_iterator(qs):

                    # have to contruct the payee name from multiple fields
                    if q.payee_naml == '':
                        bal_name = q.bal_name
                        cand_name = (
                            '{0} {1} {2} {3}'
                            .format(
                                q.cand_namt,
                                q.cand_namf,
                                q.cand_naml,
                                q.cand_nams
                            )
                            .strip()
                        )

                        juris_name = q.juris_dscr
                        off_name = q.offic_dscr
                        name_list = [
                            bal_name, cand_name, juris_name, off_name, ]
                        recipient_name = ' '.join(name_list)
                        person_flag = False
                        raw_org_name = ''
                    else:
                        recipient_name = (
                            '{0} {1} {2} {3}'
                            .format(
                                q.payee_namt.encode('utf-8'),
                                q.payee_namf.encode('utf-8'),
                                q.payee_naml.encode('utf-8'),
                                q.payee_nams.encode('utf-8')
                            )
                            .strip()
                        )

                        if q.payee_namf == '':
                            raw_org_name = q.payee_naml
                            person_flag = False
                        else:
                            person_flag = True
                            raw_org_name = ''

                    insert = Expenditure()
                    insert.cycle = f.cycle
                    insert.committee = f.committee
                    insert.filing = f
                    insert.dupe = f.dupe
                    insert.line_item = q.line_item
                    insert.payee_namt = q.payee_namt
                    insert.payee_namf = q.payee_namf
                    insert.payee_naml = q.payee_naml
                    insert.payee_nams = q.payee_nams
                    insert.amend_id = q.amend_id
                    insert.expn_dscr = q.expn_dscr
                    insert.payee_zip4 = q.payee_zip4
                    insert.g_from_e_f = q.g_from_e_f
                    insert.payee_city = q.payee_city
                    insert.amount = q.amount
                    insert.memo_refno = q.memo_refno
                    insert.expn_code = q.expn_code
                    insert.memo_code = q.memo_code
                    insert.entity_cd = q.entity_cd
                    insert.bakref_tid = q.bakref_tid
                    insert.payee_adr1 = q.payee_adr1
                    insert.payee_adr2 = q.payee_adr2
                    insert.expn_chkno = q.expn_chkno
                    insert.form_type = q.form_type
                    insert.cmte_id = q.cmte_id
                    insert.xref_schnm = q.xref_schnm
                    insert.xref_match = q.xref_match
                    if q.expn_date:
                        insert.expn_date = q.expn_date.isoformat()
                    insert.cum_ytd = q.cum_ytd
                    insert.payee_st = q.payee_st
                    insert.tran_id = q.tran_id
                    insert.name = recipient_name.strip()
                    insert.person_flag = person_flag
                    insert.raw_org_name = raw_org_name

                    insert_obj_list.append(insert)
                    if len(insert_obj_list) == 5000:
                        Expenditure.objects.bulk_create(insert_obj_list)
                        insert_obj_list = []

                        reset_queries()
                        gc.collect()

        if len(insert_obj_list) > 0:
            Expenditure.objects.bulk_create(insert_obj_list)
            insert_obj_list = []

        cnt = Expenditure.objects.count()
        if sum(insert_stats.values()) == cnt:
            print 'loaded %s expenditures' % cnt
        else:
            print (
                'loaded {0} expenditures but {1} records queried'
                .format(cnt, sum(insert_stats.values()))
            )

        insert_stats = {}

        reset_queries()
        gc.collect()

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
