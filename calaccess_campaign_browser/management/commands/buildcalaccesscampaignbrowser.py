from django.core.management import call_command
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = 'Load data from the raw source files into consolidated tables'

    def handle(self, *args, **options):
        call_command("flushcalaccesscampaignbrowser")
        call_command("loadcalaccesscampaignfilers")
        call_command("loadcalaccesscampaignfilings")
        call_command("loadcalaccesscampaignsummaries")
        call_command("loadcalaccesscampaigncontributions")
        call_command("loadcalaccesscampaignexpenditures")
        self.success("Done!")
