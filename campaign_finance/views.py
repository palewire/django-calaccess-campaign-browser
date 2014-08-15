# Create your views here.
import csv
import json
from django.views import generic
from django.db.models import Sum, Count
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from campaign_finance.models import Filer, Committee, Filing, Expenditure, Contribution


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
        filename = ''
        response['Content-Disposition'] = 'attachment; filename=contributions.csv'
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        [writer.writerow(i) for i in data]
        return response


#
# Generic
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

#
# Views
#

class IndexView(generic.ListView):
    model = Filer
    template = 'templates/home/index.html'
    context_object_name = 'filers'


class ContributionDetailView(generic.DetailView):
    model = Contribution
    template_name = 'contribution/detail.html'


class ExpenditureDetailView(generic.DetailView):
    model = Expenditure
    template_name = 'expenditure/detail.html'


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
        context['filing_set'] = Filing.objects.filter(committee=self.object).order_by('-end_date')[:10]
        context['contribution_set'] = Contribution.objects.filter(committee=self.object).order_by('-amount')[:10]
        context['expenditure_set'] = Expenditure.objects.filter(committee=self.object).order_by('-amount')[:10]
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


class FilingDetailView(generic.DetailView):
    model = Filing
    template = 'templates/filing/detail.html'
