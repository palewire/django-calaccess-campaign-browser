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
        ('', 'None'),
    )
    party = models.CharField(
        max_length=255,
        choices=PARTY_CHOICES,
        default='',
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


class Name(AllCapsNameMixin):
    """
    Something that is named, with the key to link the name back to the
    originating table. From this we may be able to derive identities and
    disambiguate names found in the filings.
    """
    ext_pk = models.IntegerField(db_index=True)
    ext_table = models.CharField(max_length=255)
    ext_prefix = models.CharField(max_length=255)
    naml = models.CharField(max_length=255, null=True)
    namf = models.CharField(max_length=255, null=True)
    nams = models.CharField(max_length=255, null=True)
    namt = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=1023, null=True)
    prob_people = models.NullBooleanField(
        help_text='Identified as probably a person by the library at \
https://github.com/datamade/probablepeople'
    )
    identity_id = models.IntegerField(db_index=True)

    class Meta:
        app_label = 'calaccess_campaign_browser'

    def __unicode__(self):
        return unicode(self.name)


class Identity(AllCapsNameMixin):
    name = models.CharField(max_length=1023)

    class Meta:
        app_label = 'calaccess_campaign_browser'

    def __unicode__(self):
        return unicode(self.name)


class IdentityRelate(AllCapsNameMixin):
    """
    This relates two rows in the identity table to each other. There
    is a direction set by the 'from_id' and 'to_id', but the significance
    of this is determined by the relation type.

    The relation type column should probably be an enum, as there should
    be only a limited set of these.

    The first one implemented is the 'is synonym for' relation. For example:
        'Stewart Resnick' -> is synonym for -> 'Stewart A. Resnick'
        'Steward Resnick' -> is synonym for -> 'Stewart A. Resnick' (sp err?)
        'Stewart A. Resnick & Paramount Farming Company LLC'
            -> is synonym for -> 'Stewart A. Resnick'

    Other examples of relation types that can be created are:
        personId -> 'is on the Board of' -> orgId
        personId -> 'is founder of' -> orgId
        personId -> 'is an employee of' -> orgId

    All of these relations establish a many-to-many relationship between
    entities in the identity table.

    Obviously the sense of these can be reversed. If one looks from the "to_id"
    field to the "from_id" field using the 'is an employee of' relation, one
    would logically get a relation, which does not need to be separately
    stored:
        orgId -> 'employs' -> personId

    There are a few rules for this table. Enforcing these can be done in
    different ways and it is probably best not to hard-code something now.

    An example of a rule is that the 'is synonym for' relation should not
    have any transitive relations. In other words, there should be no case
    if an id A, an id B, and an id C for which it is true that:
        A -> 'is a synonym for' -> B -> 'is a synonym for' -> C
    If one tried to connect A to B, then the result should be that the
    relation is followed to C and that is the relation created. In other
    words, if one tried to create the linkages above, one should get:
        B -> 'is a synonym for' -> C
        A -> 'is a synonym for' -> C

    C is, I would suggest, a canonical name for the identities represented
    by A, B and C. In future, we can optimize the process of finding the
    canonical names in the table. For now, one has to ask for ids which
    do not have a 'is synonym for' relation to other ids.

    Other relations will have different rules.

    We may want columns for 'effective_date' and 'expiry_date'. One can
    imagine the following scenario.
        'Alfred' -> 'is on the Board of' -> 'Acme Inc'
            eff: 2014-03-01, exp: null
        'Bob' -> 'is on the Board of' -> 'Acme Inc'
            eff: 2014-03-01, exp: 2014-06-01
        'Charlie' -> 'is on the Board of' -> 'Acme Inc'
            eff: 2014-05-01, exp: null
    This captures the fact that the Board of 'Acme Inc' was 2 people
    on April 1, 2014 (Alfred and Bob), was 3 people on May 31, 2014
    (Alfred, Bob and Charlie) and is now 2 people (Alfred and Charlie).
    Bob obviously did not work out. For some relations, values for the
    dates would not be necessary.

    One interesting relation might be
        personId -> 'is authorized to withdraw money from' -> orgId
    For example, Ron Calderon has 5 committees he can withdraw money
    from. Two are committees created by him, one is a committee of
    an LA Council member and two are organizations he is on the Board
    of. FYI, as of now, this information is not stored anywhere.

    The updater column is a link to the User table, so that users can
    create these linkages and this can be tracked.
    """
    from_id = models.IntegerField(db_index=True)
    to_id = models.IntegerField(db_index=True)
    relation_type = models.CharField(max_length=15, null=False)
    updated = models.DateField(null=False)
    updater = models.IntegerField(null=False)

    class Meta:
        app_label = 'calaccess_campaign_browser'
        db_table = 'identity_relate'
        unique_together = ('from_id', 'to_id', 'relation_type')


class User(AllCapsNameMixin):
    userid = models.IntegerField(null=False)
    username = models.CharField(max_length=31, null=False)

    class Meta:
        app_label = 'calaccess_campaign_browser'


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
