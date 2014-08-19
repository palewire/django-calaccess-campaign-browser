import gc

from django.core.management.base import BaseCommand
from django.db import reset_queries
from django.db.models import Q

try:
    from calaccess_raw.models import (
        FilernameCd,
        FilerFilingsCd,
        FilerLinksCd,
        ExpnCd, RcptCd,
        SmryCd
    )

except:
    print 'you need to load the raw calaccess data app'

from calaccess_campaign_browser.models import (
    Committee,
    Contribution,
    Cycle,
    Expenditure,
    Filer,
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
        self.load_filers()
        self.load_filings()
        self.load_summary()
        self.load_contributions()
        self.load_expenditures()

    def load_filers(self):
        '''
        Take a look in the Filings table and just
        load up the filers that have filed a 460 or a 450.
        Load the candidates first,
        linking them to all the committees they control.
        Then load the rest of the committees.
        '''
        candidate_cmte_list = []
        # all filers of type candidate
        all_candidate_filer_ids = (
            FilernameCd
            .objects
            .filter(filer_type='CANDIDATE/OFFICEHOLDER')
            .values_list('filer_id', flat=True)
            .distinct()
        )

        for filer_id in all_candidate_filer_ids:
            # querying by filer_id_a gets list of
            # connected recipient committees
            qs_linked = (
                FilerLinksCd
                .objects
                .filter(Q(filer_id_a=filer_id) | Q(filer_id_b=filer_id))
                .filter(link_type='12011')
            )

            filer_a_ids = list(
                (
                    qs_linked
                    .values_list('filer_id_a', flat=True)
                    .exclude(filer_id_a=filer_id)
                )
            )

            filer_b_ids = list(
                (
                    qs_linked
                    .values_list('filer_id_b', flat=True)
                    .exclude(filer_id_b=filer_id)
                )
            )

            cmte_filer_ids = filer_a_ids + filer_b_ids

            if len(cmte_filer_ids) > 0:  # has a linked committee
                # build a list of all candidate committees so can exclude for
                # pac import
                candidate_cmte_list.extend(cmte_filer_ids)
                # query to see if there are any filings associated with the
                # committee
                qs_cmte_filings = FilerFilingsCd.objects.filter(
                    filer_id__in=cmte_filer_ids)
                # has data associated with a committee
                if qs_cmte_filings.count() > 0:
                    candidate_filer_name_obj = (
                        FilernameCd
                        .objects
                        .filter(filer_id=filer_id)
                        .order_by('-effect_dt')
                        .exclude(naml='')[0]
                    )

                    candidate_filer_obj, created = Filer.objects.get_or_create(
                        filer_id=filer_id,
                        status=candidate_filer_name_obj.status,
                        filer_type='cand',
                        effective_date=candidate_filer_name_obj.effect_dt,
                        xref_filer_id=candidate_filer_name_obj.xref_filer_id,
                        name=(
                            '{0} {1} {2} {3}'
                            .format(
                                candidate_filer_name_obj.namt,
                                candidate_filer_name_obj.namf,
                                candidate_filer_name_obj.naml,
                                candidate_filer_name_obj.nams
                            )
                            .strip()
                        )
                    )

                    if created:
                        for cmte_filer_id in cmte_filer_ids:
                            qs_this_cmte_filings = (
                                qs_cmte_filings
                                .filter(filer_id=cmte_filer_id)
                                .values_list('filing_id', flat=True)
                            )

                            # filings have data
                            summary_count = (
                                SmryCd
                                .objects
                                .filter(
                                    filing_id__in=(
                                        list(qs_this_cmte_filings)
                                    )
                                )
                                .count()
                            )

                            if summary_count > 0:
                                candidate_filer_obj.active = True
                                candidate_filer_obj.save()

                                qs_names = (
                                    FilernameCd
                                    .objects
                                    .filter(filer_id=cmte_filer_id)
                                    .order_by('-effect_dt')
                                    .exclude(naml='')
                                )

                                if qs_names.count() > 0:
                                    cmte_filer_name_obj = qs_names[0]

                                    cmte_obj, cmte_created = (
                                        Committee
                                        .objects
                                        .get_or_create(
                                            filer=candidate_filer_obj,
                                            filer_id_raw=cmte_filer_id,
                                            name=(
                                                '{0} {1} {2} {3}'
                                                .format(
                                                    cmte_filer_name_obj.namt,
                                                    cmte_filer_name_obj.namf,
                                                    cmte_filer_name_obj.naml,
                                                    cmte_filer_name_obj.nams
                                                )
                                                .strip()
                                            ),
                                            committee_type='cand',
                                        )
                                    )

        print 'candidates and their linked committees loaded'

        all_filings = (
            FilerFilingsCd
            .objects
            .filter(Q(form_id='F460') | Q(form_id='F450'))
            .values_list('filing_id', flat=True)
            .distinct()
        )

        all_filings_with_data = (
            SmryCd
            .objects
            .filter(filing_id__in=all_filings)
            .values_list('filing_id', flat=True)
            .distinct()
        )

        # if you swap filing_id for filer_id in the values clause you
        # get the same count of filings as in all_filings_with_data
        all_filers_with_data = (
            FilerFilingsCd
            .objects
            .filter(filing_id__in=all_filings_with_data)
            .exclude(filer_id__in=candidate_cmte_list)
            .values_list('filer_id', flat=True)
            .distinct()
        )

        for pac_filer_id in all_filers_with_data:
            pac_filer_name = FilernameCd.objects.filter(filer_id=pac_filer_id)

            if pac_filer_name.count() > 0:
                pac_filer_name_obj = pac_filer_name.order_by(
                    '-effect_dt').exclude(naml='')[0]

                pac_filer_obj, created = Filer.objects.get_or_create(
                    filer_id=pac_filer_id,
                    status=pac_filer_name_obj.status,
                    filer_type='pac',
                    effective_date=pac_filer_name_obj.effect_dt,
                    xref_filer_id=pac_filer_name_obj.xref_filer_id,
                    name=(
                        '{0} {1} {2} {3}'
                        .format(
                            pac_filer_name_obj.namt,
                            pac_filer_name_obj.namf,
                            pac_filer_name_obj.naml,
                            pac_filer_name_obj.nams
                        )
                        .strip()
                    ),
                )
                qs_pac_filings = FilerFilingsCd.objects.filter(
                    filer_id=pac_filer_id)

                if qs_pac_filings.count() > 0:
                    qs_pac_smry = (
                        SmryCd
                        .objects
                        .filter(
                            filing_id__in=(
                                list(
                                    qs_pac_filings
                                    .values_list('filing_id', flat=True)
                                )
                            )
                        )
                    )

                    if qs_pac_smry.count() > 0:
                        pac_filer_obj.active = True
                        pac_filer_obj.save()

                pac_cmte_obj, pac_created = Committee.objects.get_or_create(
                    filer=pac_filer_obj,
                    filer_id_raw=pac_filer_id,
                    name=(
                        '{0} {1} {2} {3}'
                        .format(
                            pac_filer_name_obj.namt,
                            pac_filer_name_obj.namf,
                            pac_filer_name_obj.naml,
                            pac_filer_name_obj.nams
                        )
                        .strip()
                    ),
                    committee_type = 'pac',
                )

        print 'loaded non-candidate linked committees with associated filings'
    # Need to fix duped committee issue and deal with controlling filer thing.

    def load_filings(self):
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
