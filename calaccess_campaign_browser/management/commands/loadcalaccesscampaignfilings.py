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
        print "- Marking duplicates"
        c = connection.cursor()

        # Mark all recurring filing ids as duplicates
        sql = """CREATE TABLE tmp_filing_dupes (filing_id_raw int);"""
        c.execute(sql)

        sql = """
        INSERT INTO tmp_filing_dupes (filing_id_raw)
        SELECT filing_id_raw
        FROM calaccess_campaign_browser_filing
        GROUP BY 1
        HAVING COUNT(*) > 1;
        """
        c.execute(sql)

        sql = """
        UPDATE calaccess_campaign_browser_filing
        INNER JOIN tmp_filing_dupes
        ON calaccess_campaign_browser_filing.`filing_id_raw` = tmp_filing_dupes.`filing_id_raw`
        SET dupe = true;
        """
        c.execute(sql)

        sql = """DROP TABLE tmp_filing_dupes;"""
        c.execute(sql)

        # Unmark all those with the maximum id number among their set
        sql = """CREATE TABLE tmp_filing_max_dupes (filing_id_raw int, max_id int);"""
        c.execute(sql)

        sql = """
        INSERT INTO tmp_filing_max_dupes (filing_id_raw, max_id)
        SELECT f.`filing_id_raw`, MAX(`id`) as max_id
        FROM calaccess_campaign_browser_filing as f
        WHERE dupe = true
        GROUP BY 1
        """
        c.execute(sql)

        sql = """
        UPDATE calaccess_campaign_browser_filing
        INNER JOIN tmp_filing_max_dupes
        ON calaccess_campaign_browser_filing.`id` = tmp_filing_max_dupes.`max_id`
        SET dupe = false;
        """
        c.execute(sql)

        sql = """DROP TABLE tmp_filing_max_dupes;"""
        c.execute(sql)
