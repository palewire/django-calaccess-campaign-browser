from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load data from the raw source files into consolidated tables'

    def handle(self, *args, **options):
        call_command("loadcalaccesscampaignfilers")
        call_command("loadcalaccesscampaignfilings")
        call_command("loadcalaccesscampaignsummaries")
        call_command("loadcalaccesscampaigncontributions")
        call_command("loadcalaccesscampaignexpenditures")
