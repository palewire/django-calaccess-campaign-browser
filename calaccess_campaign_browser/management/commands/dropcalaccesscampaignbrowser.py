from django.db import connection
from calaccess_campaign_browser import models
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = "Drops all CAL-ACCESS campaign browser database tables"

    def handle(self, *args, **options):
        self.header("Dropping CAL-ACCESS campaign browser database tables")
        self.cursor = connection.cursor()

        # Ignore MySQL "note" warnings so this can be run with DEBUG=True
        self.cursor.execute("""SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0;""")

        # Loop through the models and drop all the tables
        model_list = [
            models.Contribution,
            models.Expenditure,
            models.Summary,
            models.Filing,
            models.FilingPeriod,
            models.Committee,
            models.Filer,
            models.Cycle,
            models.Election,
            models.Office,
            models.Candidate,
            models.Proposition,
            models.PropositionFiler,
        ]
        sql = """DROP TABLE IF EXISTS `%s`;"""
        for m in model_list:
            self.log(" %s" % m.__name__)
            self.cursor.execute(sql % m._meta.db_table)

        # Revert database to default "note" warning behavior
        self.cursor.execute("""SET SQL_NOTES=@OLD_SQL_NOTES;""")
