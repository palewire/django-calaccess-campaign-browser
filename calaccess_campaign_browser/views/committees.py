from django.views import generic
from .base import CommitteeDataView
from calaccess_campaign_browser.models import (
    Committee,
    Filing,
    Expenditure,
    Contribution
)


class CommitteeDetailView(generic.DetailView):
    model = Committee

    def get_context_data(self, **kwargs):
        context = super(CommitteeDetailView, self).get_context_data(**kwargs)
        context['committee'] = self.object

        # Filings
        filing_qs = Filing.real.by_committee(
            self.object,
        ).select_related("cycle", "period").order_by(
            "-end_date", "filing_id_raw", "-amend_id"
        )
        context['filing_set_short'] = filing_qs[:25]
        context['filing_set_count'] = filing_qs.count()

        # Contributions
        contribs_qs = Contribution.real.by_committee_to(self.object)
        context['contribs_set_short'] = contribs_qs.order_by('-amount')[:25]
        context['contribs_set_count'] = contribs_qs.count()

        # Transfer to other committees
        contribs_out = Contribution.real.by_committee_from(self.object)
        context['contribs_out_list'] = contribs_out.order_by('-amount')[:25]
        context['contribs_out_set_count'] = contribs_out.count()

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
        return Contribution.real.by_committee_to(
            self.committee,
        ).order_by("-date_received")


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
        return Filing.real.by_committee(committee).order_by('-date_filed')
