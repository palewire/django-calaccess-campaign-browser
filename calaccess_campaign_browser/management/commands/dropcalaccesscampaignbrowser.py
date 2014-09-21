from django.db import connection
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        c = connection.cursor()
        print "Dropping campaign browser database tables"
        sql = """
            BEGIN;
            DROP TABLE IF EXISTS `calaccess_campaign_browser_contribution`;
            DROP TABLE IF EXISTS `calaccess_campaign_browser_expenditure`;
            DROP TABLE IF EXISTS `calaccess_campaign_browser_summary`;
            DROP TABLE IF EXISTS `calaccess_campaign_browser_filing`;
            DROP TABLE IF EXISTS `calaccess_campaign_browser_filingperiod`;
            DROP TABLE IF EXISTS `calaccess_campaign_browser_cycle`;
            DROP TABLE IF EXISTS `calaccess_campaign_browser_committee`;
            DROP TABLE IF EXISTS `calaccess_campaign_browser_stats`;
            DROP TABLE IF EXISTS `calaccess_campaign_browser_filer`;
            COMMIT;
        """
        c.execute(sql)

