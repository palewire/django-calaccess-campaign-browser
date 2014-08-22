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
        """ % (
            Filing._meta.db_table,
        )
        c.execute(sql)

    def mark_duplicates(self):
        pass

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
