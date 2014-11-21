import csv
import json
from django.views import generic
from django.http import HttpResponse
from django.utils.encoding import smart_text


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
            d = dict((field_names[i], val) for i, val in enumerate(i))
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
        Returns a CSV file response, transforming 'context'
        to make the payload.
        """
        data, fields = self.prep_context_for_serialization(context)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=download.csv'
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        [writer.writerow(i) for i in data]
        return response


class CommitteeDataView(JSONResponseMixin, CSVResponseMixin, generic.ListView):
    """
    Custom generic view for our committee specific data pages
    """
    allow_empty = False
    paginate_by = 100

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
        return super(CommitteeDataView, self).render_to_response(
            context, **kwargs
        )
