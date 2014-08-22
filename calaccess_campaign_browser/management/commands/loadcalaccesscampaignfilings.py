from django.db import connection
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.models import Cycle, Filing


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Loads raw filings into consolidated tables
        """
        c = connection.cursor()
        c.execute('DELETE FROM %s' % Filing._meta.db_table)
        c.execute('DELETE FROM %s' % Cycle._meta.db_table)
        self.load_cycles()
        self.load_filings()
        self.mark_duplicates()

    def load_cycles(self):
        print "- Loading cycles"
        c = connection.cursor()
        sql = """
            INSERT INTO %s (`name`)
            SELECT `session_id`
            FROM FILER_FILINGS_CD
            GROUP BY 1
            ORDER BY 1 DESC;
        """ % (
            Cycle._meta.db_table,
        )
        c.execute(sql)

    def load_filings(self):
        print "- Loading filings"
        c = connection.cursor()
        sql = """
        INSERT INTO %s (
          cycle_id,
          committee_id,
          filing_id_raw,
          form_id,
          amend_id,
          start_date,
          end_date,
          dupe
        )
        SELECT 
          cycle.id as cycle_id,
          c.id as committee_id,
          ff.FILING_ID as filing_id_raw,
          ff.form_id as form_id,
          ff.filing_sequence as amend_id,
          ff.rpt_start as start_date,
          ff.rpt_end as end_date,
          false
        FROM FILER_FILINGS_CD as ff
        INNER JOIN calaccess_campaign_browser_committee as c
        ON ff.`filer_id` = c.`filer_id_raw`
        INNER JOIN calaccess_campaign_browser_cycle as cycle
        ON ff.session_id = cycle.name
        WHERE `FORM_ID` IN ('F450', 'F460')
        LIMIT 500;
        """ % (
            Filing._meta.db_table,
        )
        c.execute(sql)

    def mark_duplicates(self):
        pass

#    def oldschool(self, *args, **options):
#        '''
#        Loads all filings, using the most current, amended filing
#        '''
#        insert_obj_list = []

#        for c in queryset_iterator(Committee.objects.all()):
#            qs_filings = FilerFilingsCd.objects.filter(
#                Q(form_id='F460') | Q(form_id='F450'), filer_id=c.filer_id_raw)

#            filing_ids = (
#                qs_filings
#                .values_list('filing_id', flat=True)
#                .distinct()
#            )

#            for f_id in filing_ids:

#                current_filing = qs_filings.filter(
#                    filing_id=f_id).order_by('-filing_sequence')[0]

#                summary_count = (
#                    SmryCd
#                    .objects
#                    .filter(filing_id=current_filing.filing_id)
#                    .count()
#                )

#                if summary_count > 0:
#                    insert = Filing()
#                    if current_filing.session_id % 2 == 0:
#                        cycle_year = current_filing.session_id
#                    else:
#                        cycle_year = current_filing.session_id + 1
#                    insert.cycle, created = Cycle.objects.get_or_create(
#                        name=cycle_year)
#                    insert.committee = c
#                    insert.filing_id_raw = current_filing.filing_id
#                    insert.amend_id = current_filing.filing_sequence
#                    insert.form_id = current_filing.form_id

#                    if current_filing.rpt_start:
#                        insert.start_date = (
#                            current_filing
#                            .rpt_start
#                            .isoformat()
#                        )

#                    if current_filing.rpt_end:
#                        insert.end_date = (
#                            current_filing
#                            .rpt_end
#                            .isoformat()
#                        )

#                    insert_obj_list.append(insert)

#                    if len(insert_obj_list) == 5000:
#                        Filing.objects.bulk_create(insert_obj_list)
#                        insert_obj_list = []

#        if len(insert_obj_list) > 0:
#            Filing.objects.bulk_create(insert_obj_list)
#            insert_obj_list = []

#        print 'loaded filings'
#        gc.collect()
#        reset_queries()

#        # get dupe filings flagged
#        d = {}
#        for f in Filing.objects.all():
#            id_num = f.filing_id_raw
#            if id_num not in d:
#                d[id_num] = 1
#            else:
#                d[id_num] += 1

#        filing_id_list = []
#        for k, v in d.items():
#            if v > 1:
#                filing_id_list.append(k)
#                # print '%s\t%s' % (k,v)

#        for id_num in filing_id_list:
#            qs = Filing.objects.filter(filing_id_raw=id_num).order_by('-id')
#            keeper = qs[0]
#            for q in qs.exclude(id=keeper.id):
#                q.dupe = True
#                q.save()

#        print 'flagged dupe filings'
#        gc.collect()
#        reset_queries()
