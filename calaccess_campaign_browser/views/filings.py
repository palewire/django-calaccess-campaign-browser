import datetime
from .search import get_query
from django.views import generic
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from calaccess_campaign_browser.models import Filer, Filing


class LatestFilingView(generic.ListView):
    template_name = 'calaccess_campaign_browser/latest.html'

    def get_queryset(self, *args, **kwargs):
        next_year = datetime.date.today() + datetime.timedelta(days=365)
        return Filing.objects.exclude(
            date_filed__gt=next_year
        ).select_related("committee").order_by("-date_filed")[:500]


class FilerListView(generic.ListView):
    template_name = "filer_list"
    allow_empty = True
    paginate_by = 100

    def get_queryset(self):
        qs = Filer.objects.exclude(name="")
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query = get_query(self.request.GET['q'], [
                'name', 'filer_id_raw', 'xref_filer_id'
            ])
            qs = qs.filter(query)
        if ('t' in self.request.GET) and self.request.GET['t'].strip():
            qs = qs.filter(filer_type=self.request.GET['t'])
        if ('p' in self.request.GET) and self.request.GET['p'].strip():
            qs = qs.filter(party=self.request.GET['p'])
        return qs

    def get_context_data(self, **kwargs):
        context = super(FilerListView, self).get_context_data(**kwargs)
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            context['query_string'] = self.request.GET['q']
        if ('t' in self.request.GET) and self.request.GET['t'].strip():
            context['type'] = self.request.GET['t']
        if ('p' in self.request.GET) and self.request.GET['p'].strip():
            context['party'] = self.request.GET['p']
        context.update(dict(
            base_url=reverse("filer_list"),
            type_list=sorted(Filer.FILER_TYPE_CHOICES, key=lambda x: x[1]),
            party_list=sorted(Filer.PARTY_CHOICES, key=lambda x: x[1]),
        ))
        return context


class FilingDetailView(generic.DetailView):
    model = Filing


class FilerDetailView(generic.DetailView):
    model = Filer

    def get_context_data(self, **kwargs):
        context = super(FilerDetailView, self).get_context_data(**kwargs)
        context['contributions_total'] = sum([
            i.total_contributions for i in self.object.committee_set.all()
        ])
        context['expenditures_total'] = sum([
            i.total_expenditures for i in self.object.committee_set.all()
        ])
        return context

    def render_to_response(self, context):
        if context['object'].committee_set.count() == 1:
            return redirect(
                context['object'].committee_set.all()[0].get_absolute_url()
            )
        return super(FilerDetailView, self).render_to_response(context)
