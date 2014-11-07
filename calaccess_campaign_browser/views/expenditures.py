from django.views import generic
from calaccess_campaign_browser.models import Expenditure


class ExpenditureDetailView(generic.DetailView):
    model = Expenditure
