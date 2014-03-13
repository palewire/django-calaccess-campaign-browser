# Create your views here.
from django.shortcuts import get_list_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from campaign_finance.models import *

class FilerListView(generic.ListView):
    model = Filer
    template = 'templates/filer/list.html'
    context_object_name = 'filers'

    # def get_queryset(self):
    #     qs = Filer.objects.filter(filer_type='cand')
    #     return qs

class FilerDetailView(generic.DetailView):
    model = Filer
    template = 'templates/filer/detail.html'

# class CommitteeListView(generic.ListView):
#     model = Committee
#     template = 'templates/committee/list.html'
#     context_object_name = 'committees'

class CommitteeDetailView(generic.DetailView):
    model = Committee
    template = 'templates/committee/detail.html'

# class FilingListView(generic.ListView):
#     model = Filing
#     template = 'templates/filing/list.html'
#     context_object_name = 'filings'

class FilingDetailView(generic.DetailView):
    model = Filing
    template = 'templates/filing/detail.html'