from django.views import generic

class PartyListView(generic.TemplateView):
    template_name = "party_list"