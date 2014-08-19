import gc
from django.db import reset_queries
from calaccess_raw.models import ExpnCd
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.models import Expenditure, Filing
from calaccess_campaign_browser.utils.querysetiterator import queryset_iterator


class Command(BaseCommand):

    def handle(self):
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
