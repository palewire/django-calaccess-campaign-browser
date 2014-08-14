# Create your views here.
import csv
import json
from django.views import generic
from django.db.models import Sum, Count
from django.http import Http404, HttpResponse
from campaign_finance.models import Filer, Committee, Filing
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class CSVResponseMixin(object):
    """
    A mixin that can be used to render a CSV response.
    """
    def render_to_response(self, context, **response_kwargs):
        """
        Returns a CSV file response, transforming 'context' to make the payload.
        """
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=contributions.csv'
        field_names = context[0].keys()
        writer = csv.DictWriter(response, fieldnames=field_names)
        writer.writeheader()
        [writer.writerow(i) for i in context]
        return response



class FilerListView(generic.ListView):
    model = Filer
    template = 'templates/filer/list.html'
    context_object_name = 'filers'
    allow_empty = False
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(FilerListView, self).get_context_data(**kwargs)
        return context


class FilerDetailView(generic.DetailView):
    model = Filer
    template = 'templates/filer/detail.html'


class CommitteeDetailView(generic.DetailView):
    model = Committee
    template = 'templates/committee/detail.html'


class FilingDetailView(generic.DetailView):
    model = Filing
    template = 'templates/filing/detail.html'
