import MySQLdb
import warnings
from django.db import connection
from optparse import make_option
from calaccess_campaign_browser.models import Filing, FilingPeriod
from calaccess_campaign_browser.management.commands import CalAccessCommand


custom_options = (
    make_option(
        "--flush",
        action="store_true",
        dest="flush",
        default=False,
        help="Flush table before loading data"
    ),
)


class Command(CalAccessCommand):
    help = "Load refined CAL-ACCESS campaign filings"
    option_list = CalAccessCommand.option_list + custom_options

    def handle(self, *args, **options):
        """
        Loads raw filings into consolidated tables
        """
        self.header("Loading filings")
        # Ignore MySQL warnings so this can be run with DEBUG=True
        warnings.filterwarnings("ignore", category=MySQLdb.Warning)
        if options['flush']:
            self.flush()
        self.load_periods()
        self.load_filings()
        self.mark_duplicates()

    def load_periods(self):
        self.log(" Loading filing periods")
        c = connection.cursor()
        sql = """
            INSERT INTO %(clean_table)s (
                `period_id`,
                `name`,
                `start_date`,
                `end_date`,
                `deadline`
            )
            SELECT DISTINCT
                p.`period_id`,
                p.`period_desc`,
                p.`start_date`,
                p.`end_date`,
                p.`deadline`
            FROM FILING_PERIOD_CD as p
            INNER JOIN FILER_FILINGS_CD as ff
            ON p.period_id = ff.period_id
            WHERE ff.`FORM_ID` IN ('F450', 'F460', 'F497')
        """
        sql = sql % dict(clean_table=FilingPeriod._meta.db_table)
        c.execute(sql)

    def flush(self):
        self.log(" Flushing filings and filing periods")
        c = connection.cursor()
        c.execute("""SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0;""")
        c.execute("""SET FOREIGN_KEY_CHECKS = 0;""")
        sql = """TRUNCATE `%s`;""" % (FilingPeriod._meta.db_table)
        c.execute(sql)
        sql = """TRUNCATE `%s`;""" % (Filing._meta.db_table)
        c.execute(sql)
        c.execute("""SET SQL_NOTES=@OLD_SQL_NOTES;""")
        c.execute("""SET FOREIGN_KEY_CHECKS = 1;""")

    def load_filings(self):
        self.log(" Loading form 450, 460, 497 filings")
        c = connection.cursor()
        sql = """
        INSERT INTO %(filing_table)s (
          cycle_id,
          committee_id,
          filing_id_raw,
          form_type,
          amend_id,
          period_id,
          start_date,
          end_date,
          date_received,
          date_filed,
          is_duplicate
        )
        SELECT
          cycle.name as cycle_id,
          c.id as committee_id,
          ff.FILING_ID as filing_id_raw,
          ff.form_id as form_type,
          ff.filing_sequence as amend_id,
          ff.real_period_id as period_id,
          ff.rpt_start as start_date,
          ff.rpt_end as end_date,
          ff.rpt_date as date_received,
          ff.filing_date as date_filed,
          false
        FROM (
            SELECT
                *,
                CASE
                    WHEN `session_id` %% 2 = 0 THEN `session_id`
                    ELSE `session_id` + 1
                END as cycle,
                CASE
                    WHEN `period_id` = 0 THEN null
                    ELSE `period_id`
                END as real_period_id
            FROM FILER_FILINGS_CD
        ) as ff
        INNER JOIN calaccess_campaign_browser_committee as c
        ON ff.`filer_id` = c.`filer_id_raw`
        INNER JOIN calaccess_campaign_browser_cycle as cycle
        ON ff.cycle = cycle.name
        WHERE `FORM_ID` IN ('F450', 'F460', 'F497')
        """
        sql = sql % dict(filing_table=Filing._meta.db_table)
        c.execute(sql)

    def mark_duplicates(self):
        self.log(" Marking duplicates")
        c = connection.cursor()

        sql = """
        CREATE TEMPORARY TABLE tmp_filing_dupes (
            index(`filing_id_raw`)
        ) AS (
            SELECT filing_id_raw
            FROM calaccess_campaign_browser_filing
            GROUP BY 1
            HAVING COUNT(*) > 1
        );
        """
        c.execute(sql)

        sql = """
        UPDATE calaccess_campaign_browser_filing as f
        INNER JOIN tmp_filing_dupes as d
        ON f.`filing_id_raw` = d.`filing_id_raw`
        SET is_duplicate = true;
        """
        c.execute(sql)

        sql = """DROP TABLE tmp_filing_dupes;"""
        c.execute(sql)

        # Unmark all those with the maximum id number among their set
        sql = """
        CREATE TEMPORARY TABLE tmp_filing_max_dupes (
            index(`filing_id_raw`),
            index(`max_id`)
        ) AS (
            SELECT f.`filing_id_raw`, MAX(`amend_id`) as max_id
            FROM calaccess_campaign_browser_filing as f
            WHERE is_duplicate = true
            GROUP BY 1
        );
        """
        c.execute(sql)

        sql = """
        UPDATE calaccess_campaign_browser_filing as f
        INNER JOIN tmp_filing_max_dupes as d
        ON f.`filing_id_raw` = d.`filing_id_raw`
        AND f.`amend_id` = d.`max_id`
        SET is_duplicate = false;
        """
        c.execute(sql)

        sql = """DROP TABLE tmp_filing_max_dupes;"""
        c.execute(sql)

        # And then anything without a period should go down as a dupe too
        Filing.objects.filter(period_id=None).update(is_duplicate=True)
