from django.views import generic

class PartyListView(generic.ListView):
    template_name = "party_list"