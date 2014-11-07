from django.views import generic
from calaccess_campaign_browser.models import Contribution


class ContributionDetailView(generic.DetailView):
    model = Contribution
