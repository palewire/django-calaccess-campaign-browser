import datetime
from .base import CommitteeDataView
from django.views import generic
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from calaccess_campaign_browser.models import (
    Filer,
    Committee,
    Filing,
    Expenditure,
    Contribution
)

NEXT_YEAR = datetime.date.today() + datetime.timedelta(days=365)


class LatestView(generic.ListView):
    template_name = 'calaccess_campaign_browser/latest.html'
    queryset = Filing.objects.exclude(
        date_filed__gt=NEXT_YEAR
    ).select_related("committee").order_by("-date_filed")[:100]


class FilerListView(generic.ListView):
    template_name = "filer_list"
    allow_empty = True
    paginate_by = 100

    def get_queryset(self):
        qs = Filer.objects.exclude(name="")
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query = get_query(self.request.GET['q'], [
                'name', 'filer_id', 'xref_filer_id'
            ])
            qs = qs.filter(query)
        return qs

    def get_context_data(self, **kwargs):
        context = super(FilerListView, self).get_context_data(**kwargs)
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            context['query_string'] = self.request.GET['q']
        context['base_url'] = reverse("filer_list")
        return context


class ContributionDetailView(generic.DetailView):
    model = Contribution


class ExpenditureDetailView(generic.DetailView):
    model = Expenditure


class FilingDetailView(generic.DetailView):
    model = Filing


class FilerDetailView(generic.DetailView):
    model = Filer

    def render_to_response(self, context):
        if context['object'].committee_set.count() == 1:
            return redirect(
                context['object'].committee_set.all()[0].get_absolute_url()
            )
        return super(FilerDetailView, self).render_to_response(context)


class CommitteeDetailView(generic.DetailView):
    model = Committee

    def get_context_data(self, **kwargs):
        context = super(CommitteeDetailView, self).get_context_data(**kwargs)
        context['committee'] = self.object

        # Filings
        filing_qs = Filing.real.filter(
            committee=self.object,
        ).select_related("cycle", "period").order_by(
            "-end_date", "filing_id_raw", "-amend_id"
        )
        context['filing_set_short'] = filing_qs[:25]
        context['filing_set_count'] = filing_qs.count()

        # Contributions
        contribs_qs = Contribution.real.filter(committee=self.object)
        context['contribution_set_short'] = contribs_qs.order_by('-amount')[:25]
        context['contribution_set_count'] = contribs_qs.count()

        # Expenditures
        expends_qs = Expenditure.objects.filter(
            committee=self.object,
            dupe=False
        )
        context['expenditure_set_short'] = expends_qs.order_by('-amount')[:25]
        context['expenditure_set_count'] = expends_qs.count()

        # Close out
        return context


class CommitteeContributionView(CommitteeDataView):
    model = Contribution
    template_name = 'calaccess_campaign_browser/committee_\
contribution_list.html'
    context_object_name = 'committee_contributions'

    def get_queryset(self):
        """
        Returns the contributions related to this committee.
        """
        committee = Committee.objects.get(pk=self.kwargs['pk'])
        self.committee = committee
        return committee.contribution_set.all().order_by('-rcpt_date')


class CommitteeExpenditureView(CommitteeDataView):
    model = Expenditure
    template_name = 'calaccess_campaign_browser/committee_\
expenditure_list.html'
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
    template_name = 'calaccess_campaign_browser/committee_filing_list.html'
    context_object_name = 'committee_filings'

    def get_queryset(self):
        """
        Returns the expends related to this committee.
        """
        committee = Committee.objects.get(pk=self.kwargs['pk'])
        self.committee = committee
        return committee.filing_set.filter(
            is_duplicate=False
        ).order_by('-date_filed')
