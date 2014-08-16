# Create your views here.
import re
import csv
import json
from django.db.models import Q
from django.views import generic
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger
)

from bakery.views import BuildableListView

from campaign_finance.models import (
    Filer,
    Committee,
    Filing,
    Expenditure,
    Contribution,
    FlatFile
)


#
# Mixins
#


class DataPrepMixin(object):
    """
    Provides a method for preping a context object
    for serialization as JSON or CSV.
    """
    def prep_context_for_serialization(self, context):
        field_names = self.model._meta.get_all_field_names()
        values = self.get_queryset().values_list(*field_names)
        data_list = []
        for i in values:
            d = {field_names[index]:val for index, val in enumerate(i)}
            data_list.append(d)

        return (data_list, field_names)


class JSONResponseMixin(DataPrepMixin):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        data, fields = self.prep_context_for_serialization(context)
        return HttpResponse(
            json.dumps(data, default=smart_text),
            content_type='application/json',
            **response_kwargs
        )


class CSVResponseMixin(DataPrepMixin):
    """
    A mixin that can be used to render a CSV response.
    """
    def render_to_csv_response(self, context, **response_kwargs):
        """
        Returns a CSV file response, transforming 'context' to make the payload.
        """
        data, fields = self.prep_context_for_serialization(context)
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=download.csv'
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        [writer.writerow(i) for i in data]
        return response


#
# Views
#


class CommitteeDataView(JSONResponseMixin, CSVResponseMixin, generic.ListView):
    """
    Custom generic view for our committee specific data pages
    """
    allow_empty = False
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(CommitteeDataView, self).get_context_data(**kwargs)
        context['committee'] = self.committee
        context['base_url'] = self.committee.get_absolute_url
        return context

    def render_to_response(self, context, **kwargs):
        """
        Return a normal response, or CSV or JSON depending
        on a URL param from the user.
        """
        # See if the user has requested a special format
        format = self.request.GET.get('format', '')
        # If it's a CSV
        if 'csv' in format:
            return self.render_to_csv_response(context)

        # If it's JSON
        if 'json' in format:
            return self.render_to_json_response(context)

        # And if it's none of the above return something normal
        return super(CommitteeDataView, self).render_to_response(context, **kwargs)


class IndexView(BuildableListView):
    model = FlatFile
    template_name = 'home/index.html'
    context_object_name = 'files'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['bulk_download'] = FlatFile.objects.filter(
            file_name='bulk_campaign_finance.zip')
        return context

    def get_queryset(self):
        """
        Returns the contributions related to this committee.
        """
        files = FlatFile.objects.all().exclude(file_name='bulk_campaign_finance.zip')
        return files


class ContributionDetailView(generic.DetailView):
    model = Contribution
    template_name = 'contribution/detail.html'


class ExpenditureDetailView(generic.DetailView):
    model = Expenditure
    template_name = 'expenditure/detail.html'


class FilingDetailView(generic.DetailView):
    model = Filing
    template = 'templates/filing/detail.html'


class FilerListView(generic.ListView):
    model = Filer
    template = 'templates/filer/list.html'
    context_object_name = 'filers'
    allow_empty = False
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(FilerListView, self).get_context_data(**kwargs)
        context['base_url'] = '/explore/'
        return context


class FilerDetailView(generic.DetailView):
    model = Filer
    template = 'templates/filer/detail.html'


class CommitteeDetailView(generic.DetailView):
    model = Committee
    # context_object_name = 'committee'

    def get_context_data(self, **kwargs):
        context = super(CommitteeDetailView, self).get_context_data(**kwargs)
        context['committee'] = self.object
        context['filing_set'] = Filing.objects.filter(committee=self.object).order_by('-end_date')
        context['filing_set_short'] = context['filing_set'][:10]
        context['contribution_set'] = Contribution.objects.filter(committee=self.object).order_by('-amount')
        context['contribution_set_short'] = context['contribution_set'][:10]
        context['expenditure_set'] = Expenditure.objects.filter(committee=self.object).order_by('-amount')
        context['expenditure_set_short'] = context['expenditure_set'][:10]
        return context


class CommitteeContributionView(CommitteeDataView):
    model = Contribution
    context_object_name = 'committee_contributions'

    def get_queryset(self):
        """
        Returns the contributions related to this committee.
        """
        committee = Committee.objects.get(pk=self.kwargs['pk'])
        self.committee = committee
        return committee.contribution_set.all().order_by('-cycle')


class CommitteeExpenditureView(CommitteeDataView):
    model = Expenditure
    context_object_name = 'committee_expenditures'

    def get_queryset(self):
        """
        Returns the expends related to this committee.
        """
        committee = Committee.objects.get(pk=self.kwargs['pk'])
        self.committee = committee
        return committee.expenditure_set.all().order_by('-cycle')


class CommitteeFilingView(CommitteeDataView):
    model = Filing
    context_object_name = 'committee_filings'

    def get_queryset(self):
        """
        Returns the expends related to this committee.
        """
        committee = Committee.objects.get(pk=self.kwargs['pk'])
        self.committee = committee
        return committee.filing_set.all().order_by('-cycle')



#
# Search biz
# Taken from Julien Phalip
# http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
#

findterms=re.compile(r'"([^"]+)"|(\S+)').findall
normspace=re.compile(r'\s{2,}').sub

def normalize_query(query_string,):
    """
    Splits the query string in invidual keywords, getting rid of unecessary spaces
    and grouping quoted words together.
    Example:
    
    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    """
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    """
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    """
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def search(request):
    query_string = ''
    results = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        query = get_query(query_string, ['ctrib_city', 'ctrib_st', 'ctrib_zip4',
            'ctrib_namf', 'ctrib_naml', 'ctrib_emp', 'ctrib_occ'])
        results = Contribution.objects.filter(query)

    context = {
        'query_string': query_string,
        'results': results
    }

    return render(request, 'search/results.html', context)
