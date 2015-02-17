import json
import managers
from django.db import models
from django.db.models import Sum
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict
from .utils.models import AllCapsNameMixin, BaseModel
from .templatetags.calaccesscampaignbrowser import jsonify
from django.template.defaultfilters import date as dateformat


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
        choices=PARTY_CHOICES
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
    filer = models.ForeignKey(Filer)
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

    def get_absolute_url(self):
        return reverse('committee_detail', args=[str(self.pk)])

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


class Cycle(BaseModel):
    name = models.IntegerField(db_index=True, primary_key=True)

    class Meta:
        ordering = ("-name",)

    def __unicode__(self):
        return unicode(self.name)


class FilingPeriod(BaseModel):
    """
    A required quarterly reporting period for committees.
    """
    period_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=25, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    deadline = models.DateField()

    class Meta:
        ordering = ("-end_date",)

    def __unicode__(self):
        return "%s - %s" % (
            dateformat(self.start_date, "Y-m-d"),
            dateformat(self.end_date, "Y-m-d"),
        )


class Filing(models.Model):
    cycle = models.ForeignKey(Cycle)
    committee = models.ForeignKey(Committee)
    filing_id_raw = models.IntegerField('filing ID', db_index=True)
    amend_id = models.IntegerField('amendment', db_index=True)
    FORM_TYPE_CHOICES = (
        ('F497', 'F497: Late filing'),
        ('F460', 'F460: Quarterly'),
        ('F450', 'F450: Quarterly (Short)'),
    )
    form_type = models.CharField(
        max_length=7,
        db_index=True,
        choices=FORM_TYPE_CHOICES
    )
    period = models.ForeignKey(FilingPeriod, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    date_received = models.DateField(null=True)
    date_filed = models.DateField(null=True)
    is_duplicate = models.BooleanField(
        default=False,
        db_index=True,
        help_text="A record that has either been superceded by an amendment \
or was filed unnecessarily. Should be excluded from most analysis."
    )
    objects = models.Manager()
    real = managers.RealFilingManager()

    def __unicode__(self):
        return unicode(self.filing_id_raw)

    def get_absolute_url(self):
        return reverse('filing_detail', args=[str(self.pk)])

    def to_json(self):
        js = json.loads(jsonify(self))
        s = self.summary or {}
        if s:
            s = json.loads(jsonify(s))
        js['summary'] = s
        return json.dumps(js)

    def get_calaccess_pdf_url(self):
        url = "http://cal-access.ss.ca.gov/PDFGen/pdfgen.prg"
        qs = "filingid=%s&amendid=%s" % (
            self.filing_id_raw,
            self.amend_id
        )
        return "%s?%s" % (url, qs)

    def committee_short_name(self):
        return self.committee.short_name
    committee_short_name.short_description = "committee"

    @property
    def summary(self):
        try:
            return Summary.objects.get(
                filing_id_raw=self.filing_id_raw,
                amend_id=self.amend_id
            )
        except Summary.DoesNotExist:
            return None

    @property
    def is_amendment(self):
        return self.amend_id > 0

    @property
    def is_late(self):
        return self.form_type == 'F497'

    @property
    def is_quarterly(self):
        return self.form_type in ['F450', 'F460']

    @property
    def total_contributions(self):
        if self.is_quarterly:
            summary = self.summary
            if summary:
                return summary.total_contributions
            else:
                return None
        elif self.is_late:
            return Contribution.real.filter(
                filing=self
            ).aggregate(total=Sum('amount'))['total']

    @property
    def total_expenditures(self):
        if self.is_quarterly:
            summary = self.summary
            if summary:
                return summary.total_expenditures
            else:
                return None
        elif self.is_late:
            return Expenditure.real.filter(
                filing=self
            ).aggregate(total=Sum('amount'))['total']


class Summary(BaseModel):
    """
    A set of summary totals provided by a filing's cover sheet.
    """
    filing_id_raw = models.IntegerField(db_index=True)
    amend_id = models.IntegerField(db_index=True)
    itemized_monetary_contributions = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )
    unitemized_monetary_contributions = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )
    total_monetary_contributions = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )
    non_monetary_contributions = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )
    total_contributions = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )
    itemized_expenditures = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )
    unitemized_expenditures = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )
    total_expenditures = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )
    ending_cash_balance = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )
    outstanding_debts = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        default=None,
    )

    class Meta:
        verbose_name_plural = "summaries"

    def __unicode__(self):
        return unicode(self.filing_id_raw)

    @property
    def cycle(self):
        try:
            return self.filing.cycle
        except:
            return None

    @property
    def committee(self):
        try:
            return self.filing.committee
        except:
            return None

    @property
    def filing(self):
        try:
            return Filing.objects.get(
                filing_id_raw=self.filing_id_raw,
                amend_id=self.amend_id
            )
        except Filing.DoesNotExist:
            return None


class Expenditure(BaseModel):
    """
    Who got paid and how much.
    """
    EXPENDITURE_CODE_CHOICES = (
        ('CMP', 'campaign paraphernalia/misc.'),
        ('CNS', 'campaign consultants'),
        ('CTB', 'contribution (explain nonmonetary)*'),
        ('CVC', 'civic donations'),
        ('FIL', 'candidate filing/ballot fees'),
        ('FND', 'fundraising events'),
        ('IND',
         'independent expenditure supporting/opposing others (explain)*'),
        ('LEG', 'legal defense'),
        ('LIT', 'campaign literature and mailings'),
        ('MBR', 'member communications'),
        ('MTG', 'meetings and appearances'),
        ('OFC', 'office expenses'),
        ('PET', 'petition circulating'),
        ('PHO', 'phone banks'),
        ('POL', 'polling and survey research'),
        ('POS', 'postage, delivery and messenger services'),
        ('PRO', 'professional services (legal, accounting)'),
        ('PRT', 'print ads'),
        ('RAD', 'radio airtime and production costs'),
        ('RFD', 'returned contributions'),
        ('SAL', "campaign workers' salaries"),
        ('TEL', 't.v. or cable airtime and production costs'),
        ('TRC', 'candidate travel, lodging, and meals'),
        ('TRS', 'staff/spouse travel, lodging, and meals'),
        ('TSF', 'transfer between committees of the same candidate/sponsor'),
        ('VOT', 'voter registration'),
        ('WEB', 'information technology costs (internet, e-mail)'),
    )
    cycle = models.ForeignKey(Cycle)
    committee = models.ForeignKey(Committee)
    filing = models.ForeignKey(Filing)

    # Raw data fields
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    bakref_tid = models.CharField(max_length=50L, blank=True)
    cmte_id = models.CharField(max_length=9L, blank=True)
    cum_ytd = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    entity_cd = models.CharField(max_length=5L, blank=True)
    expn_chkno = models.CharField(max_length=20L, blank=True)
    expn_code = models.CharField(
        max_length=3L, blank=True,
        choices=EXPENDITURE_CODE_CHOICES
    )
    expn_date = models.DateField(null=True)
    expn_dscr = models.CharField(max_length=400L, blank=True)
    form_type = models.CharField(max_length=6L, blank=True)
    # back reference from Form 460 Schedule G to Schedule E or F
    g_from_e_f = models.CharField(max_length=1L, blank=True)
    line_item = models.IntegerField()
    memo_code = models.CharField(max_length=1L, blank=True)
    memo_refno = models.CharField(max_length=20L, blank=True)
    payee_adr1 = models.CharField(max_length=55L, blank=True)
    payee_adr2 = models.CharField(max_length=55L, blank=True)
    payee_city = models.CharField(max_length=30L, blank=True)
    payee_namf = models.CharField(max_length=255L, blank=True)
    payee_naml = models.CharField(max_length=200L, blank=True)
    payee_nams = models.CharField(max_length=10L, blank=True)
    payee_namt = models.CharField(max_length=10L, blank=True)
    payee_st = models.CharField(max_length=2L, blank=True)
    payee_zip4 = models.CharField(max_length=10L, blank=True)
    tran_id = models.CharField(max_length=20L, blank=True)
    # a related item on other schedule has the same transaction identifier.
    # "X" indicates this condition is true
    xref_match = models.CharField(max_length=1L, blank=True)
    # Related record is included on Form 460 Schedules B2 or F
    xref_schnm = models.CharField(max_length=2L, blank=True)

    # Derived fields
    name = models.CharField(max_length=255)
    raw_org_name = models.CharField(max_length=255)
    person_flag = models.BooleanField(default=False)
    org_id = models.IntegerField(null=True)
    individual_id = models.IntegerField(null=True)

    dupe = models.BooleanField(default=False)
    objects = models.Manager()
    real = managers.RealExpenditureManager()

    @property
    def raw(self):
        from calaccess_raw.models import ExpnCd
        return ExpnCd.objects.get(
            amend_id=self.amend_id,
            filing_id=self.filing_id,
            tran_id=self.tran_id,
            bakref_tid=self.bakref_tid
        )

    def get_absolute_url(self):
        return reverse('expenditure_detail', args=[str(self.pk)])


class Contribution(BaseModel):
    """
    Who gave and how much.
    """
    cycle = models.ForeignKey(Cycle)
    committee = models.ForeignKey(Committee, related_name="contributions_to")
    filing = models.ForeignKey(Filing)

    # CAL-ACCESS ids
    filing_id_raw = models.IntegerField(db_index=True)
    transaction_id = models.CharField(
        'transaction ID',
        max_length=20,
        db_index=True
    )
    amend_id = models.IntegerField('amendment', db_index=True)
    backreference_transaction_id = models.CharField(
        'backreference transaction ID',
        max_length=20,
        db_index=True
    )
    is_crossreference = models.CharField(max_length=1, blank=True)
    crossreference_schedule = models.CharField(max_length=2, blank=True)

    # Basics about the contrib
    is_duplicate = models.BooleanField(default=False)
    transaction_type = models.CharField(max_length=1, blank=True)
    date_received = models.DateField(null=True)
    contribution_description = models.CharField(max_length=90, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=14)

    # About the contributor
    contributor_full_name = models.CharField(max_length=255)
    contributor_is_person = models.BooleanField(default=False)
    contributor_committee = models.ForeignKey(
        Committee,
        null=True,
        related_name="contributions_from"
    )
    contributor_prefix = models.CharField(max_length=10, blank=True)
    contributor_first_name = models.CharField(max_length=255, blank=True)
    contributor_last_name = models.CharField(max_length=200, blank=True)
    contributor_suffix = models.CharField(max_length=10, blank=True)
    contributor_address_1 = models.CharField(max_length=55, blank=True)
    contributor_address_2 = models.CharField(max_length=55, blank=True)
    contributor_city = models.CharField(max_length=30, blank=True)
    contributor_state = models.CharField(max_length=2, blank=True)
    contributor_zipcode = models.CharField(max_length=10, blank=True)
    contributor_occupation = models.CharField(max_length=60, blank=True)
    contributor_employer = models.CharField(max_length=200, blank=True)
    contributor_selfemployed = models.CharField(max_length=1, blank=True)
    ENTITY_CODE_CHOICES = (
        ("", "None"),
        ("0", "0"),
        ("BNM", "BNM"),
        ("COM", "Recipient committee"),
        ("IND", "Individual"),
        ("OFF", "OFF"),
        ("OTH", "Other"),
        ("PTY", "Political party"),
        ("RCP", "RCP"),
        ("SCC", "Small contributor committee"),
    )
    contributor_entity_type = models.CharField(
        max_length=3,
        blank=True,
        help_text="The type of entity that made that contribution",
        choices=ENTITY_CODE_CHOICES
    )

    # About the intermediary
    intermediary_prefix = models.CharField(max_length=10, blank=True)
    intermediary_first_name = models.CharField(max_length=255, blank=True)
    intermediary_last_name = models.CharField(max_length=200, blank=True)
    intermediary_suffix = models.CharField(max_length=10, blank=True)
    intermediary_address_1 = models.CharField(max_length=55, blank=True)
    intermediary_address_2 = models.CharField(max_length=55, blank=True)
    intermediary_city = models.CharField(max_length=30, blank=True)
    intermediary_state = models.CharField(max_length=2, blank=True)
    intermediary_zipcode = models.CharField(max_length=10, blank=True)
    intermediary_occupation = models.CharField(max_length=60, blank=True)
    intermediary_employer = models.CharField(max_length=200, blank=True)
    intermediary_selfemployed = models.CharField(max_length=1, blank=True)
    intermediary_committee_id = models.CharField(max_length=9, blank=True)
    objects = models.Manager()
    real = managers.RealContributionManager()

    @property
    def raw(self):
        from calaccess_raw.models import RcptCd
        return RcptCd.objects.get(
            amend_id=self.amend_id,
            filing_id=self.filing.filing_id_raw,
            tran_id=self.transaction_id,
            bakref_tid=self.backreference_transaction_id
        )

    @property
    def contributor_dict(self):
        d = SortedDict({})
        for k, v in self.to_dict().items():
            if k.startswith("contributor"):
                d[k.replace("contributor ", "")] = v
        return d

    @property
    def intermediary_dict(self):
        d = SortedDict({})
        for k, v in self.to_dict().items():
            if k.startswith("intermediary"):
                d[k.replace("intermediary ", "")] = v
        return d

    def get_absolute_url(self):
        return reverse('contribution_detail', args=[str(self.pk)])


class Election(BaseModel):
    """
    A grouping of election contests administered by the state.
    """
    ELECTION_TYPE_CHOICES = (
        ("GENERAL", "General"),
        ("PRIMARY", "Primary"),
        ("RECALL", "Recall"),
        ("SPECIAL", "Special"),
        ("SPECIAL_RUNOFF", "Special Runoff"),
        ("OTHER", "Other"),
    )
    election_type = models.CharField(
        choices=ELECTION_TYPE_CHOICES,
        max_length=50
    )
    year = models.IntegerField()
    date = models.DateField(null=True, default=None)
    id_raw = models.IntegerField(
        verbose_name="UID (CAL-ACCESS)",
        help_text="The unique identifer from the CAL-ACCESS site"
    )
    sort_index = models.IntegerField(
        help_text="The order of the election on the CAL-ACCESS site",
    )

    class Meta:
        ordering = ('-sort_index',)

    def __unicode__(self):
        return u'%s %s' % (
            self.year,
            self.get_election_type_display(),
        )

    @property
    def office_count(self):
        """
        The total number of offices with active races this election.
        """
        return self.candidate_set.values("office_id").distinct().count()

    @property
    def candidate_count(self):
        """
        The total number of candidates fundraising for this election.
        """
        return self.candidate_set.count()


class Office(BaseModel):
    """
    An office that is at stake in an election contest.
    """
    OFFICE_CHOICES = (
        ("ASSEMBLY", "Assembly"),
        ("ATTORNEY_GENERAL", "Attorney General"),
        ("BOARD_OF_EQUALIZATION", "Board of Equalization"),
        ("CONTROLLER", "Controller"),
        ("GOVERNOR", "Governor"),
        ("INSURANCE_COMMISSIONER", "Insurance Commissioner"),
        ("LIEUTENANT_GOVERNOR", "Lieutenant Governor"),
        ("OTHER", "Other"),
        ("SECRETARY_OF_STATE", "Secretary of State"),
        ("SENATE", "Senate"),
        (
            "SUPERINTENDENT_OF_PUBLIC_INSTRUCTION",
            "Superintendent of Public Instruction"
        ),
        ("TREASURER", "Treasurer"),
    )
    name = models.CharField(
        choices=OFFICE_CHOICES,
        max_length=50
    )
    seat = models.IntegerField(null=True, default=None)

    class Meta:
        ordering = ('name', 'seat',)

    def __unicode__(self):
        s = u'%s' % (self.get_name_display(),)
        if self.seat:
            s = u'%s (%s)' % (s, self.seat)
        return s

    @property
    def election_count(self):
        """
        The total number of elections with active races this office.
        """
        return self.candidate_set.values("election_id").distinct().count()

    @property
    def candidate_count(self):
        """
        The total number of candidates who have fundraised for this office.
        """
        return self.candidate_set.count()


class Candidate(BaseModel):
    """
    Links filers to the contests and elections where they are on the ballot.
    """
    election = models.ForeignKey(Election)
    office = models.ForeignKey(Office)
    filer = models.ForeignKey(Filer)

    class Meta:
        ordering = ("election", "office", "filer")

    def __unicode__(self):
        return u'%s: %s [%s]' % (self.filer, self.office, self.election)

    @property
    def election_year(self):
        return self.election.year

    @property
    def election_name(self):
        return self.election.get_name_display()


class Proposition(BaseModel):
    """
    A proposition or ballot measure decided by voters.
    """
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True)
    id_raw = models.IntegerField(db_index=True)
    election = models.ForeignKey(Election, null=True, default=None)
    filers = models.ManyToManyField(Filer, through='PropositionFiler')

    class Meta:
        ordering = ("election", "name")

    def __unicode__(self):
        return self.name

    @property
    def short_description(self, character_limit=60):
        if len(self.description) > character_limit:
            return self.description[:character_limit] + "..."
        return self.description


class PropositionFiler(BaseModel):
    """
    The relationship between filers and propositions.
    """
    POSITION_CHOICES = (
        ('SUPPORT', 'Support'),
        ('OPPOSE', 'Oppose'),
    )
    proposition = models.ForeignKey(Proposition)
    filer = models.ForeignKey(Filer)
    position = models.CharField(
        choices=POSITION_CHOICES,
        max_length=50
    )

    def __unicode__(self):
        return '%s %s' % (self.proposition, self.filer)
