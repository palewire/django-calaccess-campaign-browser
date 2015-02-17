from django.core.management import call_command
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = 'Transforms and loads refined data from raw CAL-ACCESS source files'

    def handle(self, *args, **options):
        call_command("flushcalaccesscampaignbrowser")
        call_command("loadcalaccesscampaignfilers")
        call_command("loadcalaccesscampaignfilings")
        call_command("loadcalaccesscampaignsummaries")
        call_command("loadcalaccesscampaigncontributions")
        # call_command("loadcalaccesscampaignexpenditures")
        call_command("scrapecalaccesscampaigncandidates")
        call_command("scrapecalaccesscampaignpropositions")
        self.success("Done!")
