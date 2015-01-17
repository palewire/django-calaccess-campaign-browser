from django.views import generic


class PartyListView(generic.TemplateView):
    template_name = "calaccess_campaign_browser/party_list.html"
