from django.db import connection
from calaccess_campaign_browser import models
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):

    def handle(self, *args, **options):
        self.cursor = connection.cursor()
        self.header("Dropping CAL-ACCESS campaign browser tables")
        model_list = [
            models.Contribution,
            models.Expenditure,
            models.Summary,
            models.Filing,
            models.FilingPeriod,
            models.Cycle,
            models.Committee,
            models.Filer,
        ]
        self.cursor.execute("""SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0;""")
        sql = """DROP TABLE IF EXISTS `%s`;"""
        for m in model_list:
            self.log(" %s" % m.__name__)
            self.cursor.execute(sql % m._meta.db_table)
        self.cursor.execute("""SET SQL_NOTES=@OLD_SQL_NOTES;""")
