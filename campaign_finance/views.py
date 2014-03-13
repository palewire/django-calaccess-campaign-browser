# Create your views here.
from django.shortcuts import get_list_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from campaign_finance.models import *

class FilingListView(generic.ListView):
    model = Filing
    template = 'templates/filing/list.html'
    context_object_name = 'filings'

class FilingDetailView(generic.DetailView):
    model = Filing
    template = 'templates/filing/detail.html'