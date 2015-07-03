from .filings import Filing
from django.db import models
from django.template.defaultfilters import slugify
from calaccess_campaign_browser.utils.models import AllCapsNameMixin
import time


class Filer(AllCapsNameMixin):
    """
    An entity that files campaign finance disclosure documents.

    That includes candidates for public office that have committees raising
    money on their behalf (i.e. Jerry Brown) as well as Political Action
    Committees (PACs) that contribute money to numerous candidates for office.
    """
    name = models.CharField(max_length=255, null=True)
    filer_id_raw = models.IntegerField(db_index=True)
    xref_filer_id = models.CharField(
        max_length=32,
        null=True,
        db_index=True
    )
    FILER_TYPE_CHOICES = (
        ('pac', 'PAC'),
        ('cand', 'Candidate'),
    )
    filer_type = models.CharField(
        max_length=10,
        choices=FILER_TYPE_CHOICES
    )
    PARTY_CHOICES = (
        ('16013', 'Americans Elect'),
        ('16012', 'No party preference'),
        ('16011', 'Unknown'),
        ('16010', 'Natural law'),
        ('16009', 'Non-partisan'),
        ('16008', 'Libertarian'),
        ('16007', 'Independent'),
        ('16006', 'Peace and Freedom'),
        ('16005', 'American Independent'),
        ('16004', 'Reform'),
        ('16003', 'Green'),
        ('16002', 'Republican'),
        ('16001', 'Democratic'),
        ('0', 'N/A'),
    )
    party = models.CharField(
        max_length=255,
        choices=PARTY_CHOICES,
    )
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('N', 'Inactive'),
        ('P', 'Pending'),
        ('R', 'Revoked'),
        ('S', 'Suspended'),
        ('TERMINATED', 'Terminated'),
        ('W', 'Withdrawn'),
        ('Y', 'Active'),
    )
    status = models.CharField(
        max_length=255,
        null=True,
        choices=STATUS_CHOICES
    )
    effective_date = models.DateField(null=True)

    class Meta:
        ordering = ("name",)
        app_label = 'calaccess_campaign_browser'

    @models.permalink
    def get_absolute_url(self):
        return ('filer_detail', [str(self.pk)])

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def real_filings(self):
        return Filing.real.filter(committee__filer=self)

    @property
    def total_contributions(self):
        summaries = [f.summary for f in self.real_filings]
        summaries = [s for s in summaries if s]
        return sum([
            s.total_contributions for s in summaries if s.total_contributions
        ])


class Committee(AllCapsNameMixin):
    """
    If a Candidate controls the committee, the filer is associated with the
    Candidate Filer record, not the committee Filer record
    But the committee Filer record can still be accessed using filer_id_raw
    So candidate filers potentially link to multiple committes,
    and committee filers that are not candidate controlled
    link back to one, committee filer
    If there's a better way I'm open to suggestions
    """
    filer = models.ForeignKey('Filer')
    filer_id_raw = models.IntegerField(db_index=True)
    xref_filer_id = models.CharField(
        max_length=32,
        null=True,
        db_index=True
    )
    name = models.CharField(max_length=255, null=True)
    CMTE_TYPE_OPTIONS = (
        ('cand', 'Candidate'),
        ('pac', 'PAC'),
        ('linked-pac', 'Non-Candidate Committee, linked to other committees'),
    )
    committee_type = models.CharField(
        max_length=50,
        choices=CMTE_TYPE_OPTIONS,
        db_index=True,
    )
    PARTY_CHOICES = (
        ('16013', 'Americans Elect'),
        ('16012', 'No party preference'),
        ('16011', 'Unknown'),
        ('16010', 'Natural law'),
        ('16009', 'Non-partisan'),
        ('16008', 'Libertarian'),
        ('16007', 'Independent'),
        ('16006', 'Peace and Freedom'),
        ('16005', 'American Independent'),
        ('16004', 'Reform'),
        ('16003', 'Green'),
        ('16002', 'Republican'),
        ('16001', 'Democratic'),
        ('0', 'N/A'),
    )
    party = models.CharField(
        max_length=255,
        choices=PARTY_CHOICES
    )
    COMMITTEE_STATUS_CHOICES = (
        ('', 'N/A'),
        ('N', 'Inactive'),
        ('P', 'Pending'),
        ('R', 'Revoked'),
        ('S', 'Suspended'),
        ('W', 'Withdrawn'),
        ('Y', 'Active'),
    )
    status = models.CharField(
        max_length=255,
        null=True,
        choices=COMMITTEE_STATUS_CHOICES
    )
    LEVEL_CHOICES = (
        ('40501', 'Local'),
        ('40502', 'State'),
        ('40503', 'County'),
        ('40504', 'Multi-county'),
        ('40505', 'City'),
        ('40506', 'Federal'),
        ('40507', 'Superior court judge'),
        ('0', 'N/A'),
    )
    level_of_government = models.CharField(
        max_length=255,
        null=True,
        choices=LEVEL_CHOICES
    )
    effective_date = models.DateField(null=True)

    class Meta:
        ordering = ("name",)
        app_label = 'calaccess_campaign_browser'

    @models.permalink
    def get_absolute_url(self):
        return ('committee_detail', [str(self.pk)])

    def get_calaccess_url(self):
        url = "http://cal-access.ss.ca.gov/Campaign/Committees/Detail.aspx?id="
        return url + str(self.filer_id_raw)

    @property
    def filer_short_name(self):
        return self.filer.short_name

    @property
    def real_filings(self):
        return Filing.real.by_committee(self).select_related("cycle")

    @property
    def total_contributions(self):
        return sum([
            f.total_contributions for f in self.real_filings
            if f.total_contributions
        ])

    @property
    def total_contributions_by_year(self):
        d = {}
        for f in self.real_filings:
            if not f.total_contributions:
                continue
            try:
                d[f.period.start_date.year] += f.total_contributions
            except KeyError:
                d[f.period.start_date.year] = f.total_contributions
        return sorted(d.items(), key=lambda x: x[0], reverse=True)

    @property
    def total_contributions_by_cycle(self):
        d = {}
        for f in self.real_filings:
            if not f.total_contributions:
                continue
            try:
                d[f.cycle.name] += f.total_contributions
            except KeyError:
                d[f.cycle.name] = f.total_contributions
        return sorted(d.items(), key=lambda x: x[0], reverse=True)

    @property
    def total_expenditures(self):
        return sum([
            f.total_expenditures for f in self.real_filings
            if f.total_expenditures
        ])

    @property
    def total_expenditures_by_cycle(self):
        d = {}
        for f in self.real_filings:
            if not f.total_expenditures:
                continue
            try:
                d[f.cycle.name] += f.total_expenditures
            except KeyError:
                d[f.cycle.name] = f.total_expenditures
        return sorted(d.items(), key=lambda x: x[0], reverse=True)

    @property
    def total_expenditures_by_year(self):
        d = {}
        for f in self.real_filings:
            if not f.total_expenditures:
                continue
            try:
                d[f.period.start_date.year] += f.total_expenditures
            except KeyError:
                d[f.period.start_date.year] = f.total_expenditures
        return sorted(d.items(), key=lambda x: x[0], reverse=True)

    @property
    def total_cashflow_balance(self):
        return self.total_contributions - self.total_expenditures

    @property
    def years_active(self):
        filings = self.real_filings.all()
        if not filings:
            return None
        start_filing = filings.order_by('start_date').first().start_date.year
        end_filing = filings.order_by('end_date').last().end_date.year

        if end_filing == int(time.strftime("%Y")):
            end_filing = "Present"

        if start_filing == end_filing:
            return "(%s)" % end_filing
        else:
            return "(%s - %s)" % (start_filing, end_filing)
