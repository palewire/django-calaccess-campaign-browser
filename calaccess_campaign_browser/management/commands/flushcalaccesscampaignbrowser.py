from django.db import connection
from calaccess_campaign_browser import models
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = "Flush CAL-ACCESS campaign browser database tables"

    def handle(self, *args, **options):
        self.header("Flushing CAL-ACCESS campaign browser database tables")
        c = connection.cursor()
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
