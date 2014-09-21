from django.db import connection
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        c = connection.cursor()
        print "Flushing campaign browser database tables"
        sql = """
            BEGIN;
            SET FOREIGN_KEY_CHECKS = 0;
            TRUNCATE `calaccess_campaign_browser_filer`;
            TRUNCATE `calaccess_campaign_browser_filing`;
            TRUNCATE `calaccess_campaign_browser_stats`;
            TRUNCATE `calaccess_campaign_browser_summary`;
            TRUNCATE `calaccess_campaign_browser_filingperiod`;
            TRUNCATE `calaccess_campaign_browser_cycle`;
            TRUNCATE `calaccess_campaign_browser_committee`;
            TRUNCATE `calaccess_campaign_browser_expenditure`;
            SET FOREIGN_KEY_CHECKS = 1;
            COMMIT;
        """
        c.execute(sql)
