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


class FilerDetailView(generic.DetailView):
    model = Filer
    template = 'templates/filer/detail.html'


class CommitteeDetailView(generic.DetailView):
    model = Committee
    template = 'templates/committee/detail.html'


class FilingDetailView(generic.DetailView):
    model = Filing
    template = 'templates/filing/detail.html'
