from django.db import connection
from calaccess_campaign_browser import models
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = "Flush CAL-ACCESS campaign browser database tables"

    def handle(self, *args, **options):
        self.header("Flushing CAL-ACCESS campaign browser database tables")
        c = connection.cursor()
        c.execute("""SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0;""")
        c.execute("""SET FOREIGN_KEY_CHECKS = 0;""")
        model_list = [
            models.Filer,
            models.Filing,
            models.Summary,
            models.FilingPeriod,
            models.Cycle,
            models.Committee,
            models.Contribution,
            models.Expenditure,
            models.Election,
            models.Office,
            models.Candidate,
            models.Proposition,
            models.PropositionFiler,
        ]
        sql = """TRUNCATE `%s`;"""
        for m in model_list:
            self.log(" %s" % m.__name__)
            c.execute(sql % m._meta.db_table)
        # Revert database to default "note" warning behavior
        c.execute("""SET SQL_NOTES=@OLD_SQL_NOTES;""")
        c.execute("""SET FOREIGN_KEY_CHECKS = 1;""")
