import json

from django.views import generic
from django.utils.safestring import SafeString
from django.forms.models import model_to_dict
from .base import CommitteeDataView
from calaccess_campaign_browser.utils.lazyencoder import LazyEncoder
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

        context['committee_json'] = SafeString(
            json.dumps(model_to_dict(self.object), cls=LazyEncoder)
        )

        # Filings
        filing_qs = Filing.real.by_committee(
            self.object,
        ).select_related("cycle", "period").order_by(
            "-end_date", "filing_id_raw", "-amend_id"
        )
        context['filing_set_short'] = filing_qs[:25]
        context['filing_set_count'] = filing_qs.count()


        alist = []
        for filing in filing_qs:
            f = model_to_dict(filing)
            f['summary'] = model_to_dict( filing.summary )
            alist.append(f)

        context['filing_set_json'] = SafeString(
            json.dumps(alist, cls=LazyEncoder)
        )

        # Contributions
        contribs_qs = Contribution.real.by_committee_to(self.object)
        context['contribs_set_short'] = contribs_qs.order_by('-amount')[:25]
        context['contribs_set_count'] = contribs_qs.count()

        context['contribs_set_json'] = SafeString(
            json.dumps(
                list(contribs_qs.order_by('-amount').values()),
                cls=LazyEncoder
            )
        )

        context['contribs_by_year'] = json.dumps([
            {
                'year': year,
                'total': str(total),
            } for year, total in self.object.total_contributions_by_year
        ])

        # Transfer to other committees
        contribs_out = Contribution.real.by_committee_from(self.object)
        context['contribs_out_list'] = contribs_out.order_by('-amount')[:25]
        context['contribs_out_set_count'] = contribs_out.count()

        context['contribs_out_json'] = SafeString(
            json.dumps(
                list(contribs_out.order_by('-amount').values()),
                cls=LazyEncoder
            )
        )

        # Expenditures
        expends_qs = Expenditure.objects.filter(
            committee=self.object,
            dupe=False
        )
        context['expenditure_set_short'] = expends_qs.order_by('-amount')[:25]
        context['expenditure_set_count'] = expends_qs.count()

        context['expenditure_set_json'] = SafeString(
            json.dumps(
                list(expends_qs.order_by('-amount').values()),
                cls=LazyEncoder
            )
        )

        context['expenditure_by_year'] = json.dumps([
            {
                'year': year,
                'total': str(total),
            } for year, total in self.object.total_expenditures_by_year
        ])

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
