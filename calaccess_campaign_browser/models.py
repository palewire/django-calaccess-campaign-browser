from django.db import models
from django.db.models import Sum
from hurry.filesize import size
from django.utils.text import slugify
from .utils.models import AllCapsNameMixin
from django.core.urlresolvers import reverse


class Filer(AllCapsNameMixin):
    """
    An entity that files campaign finance disclosure documents.

    That includes candidates for public office that have committees raising
    money on their behalf (i.e. Jerry Brown) as well as Political Action
    Committees (PACs) that contribute money to numerous candidates for office.
    """
    # straight out of the filer table
    filer_id = models.IntegerField(db_index=True)
    STATUS_CHOICES = (
        ('A', 'A'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('R', 'R'),
        ('S', 'S'),
        ('TERMINATED', 'Terminated'),
        ('W', 'W'),
    )
    status = models.CharField(
        max_length=255,
        null=True,
        choices=STATUS_CHOICES
    )
    FILER_TYPE_OPTIONS = (
        ('pac', 'PAC'),
        ('cand', 'Candidate'),
    )
    filer_type = models.CharField(
        max_length=10,
        choices=FILER_TYPE_OPTIONS,
        db_index=True,
    )
    name = models.CharField(max_length=255, null=True)
    effective_date = models.DateField(null=True)
    xref_filer_id = models.CharField(
        max_length=32,
        null=True,
        db_index=True
    )

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
        return Filing.objects.filter(committee__filer=self, dupe=False)

    @property
    def total_contributions(self):
        summaries = [f.summary for f in self.real_filings]
        return sum([s.total_contributions for s in summaries if s])


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

    class Meta:
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('committee_detail', args=[str(self.pk)])

    @property
    def real_filings(self):
        return Filing.objects.filter(
            committee=self, dupe=False
        ).select_related("cycle")

    @property
    def total_contributions(self):
        summaries = [f.summary for f in self.real_filings]
        return sum([s.total_contributions for s in summaries if s])

    @property
    def total_expenditures(self):
        summaries = [f.summary for f in self.real_filings]
        return sum([s.total_expenditures for s in summaries if s])


class Cycle(models.Model):
    name = models.IntegerField(db_index=True)

    class Meta:
        ordering = ("-name",)

    def __unicode__(self):
        return unicode(self.name)


class Filing(models.Model):
    cycle = models.ForeignKey(Cycle)
    committee = models.ForeignKey(Committee)
    filing_id_raw = models.IntegerField(db_index=True)
    amend_id = models.IntegerField(db_index=True)
    FORM_ID_CHOICES = (
        ('F460', 'Recipient Committee Campaign Statement'),
        ('F450', 'Recipient Committee Campaign Statement -- Short Form'),
    )
    form_id = models.CharField(
        max_length=7,
        db_index=True,
        choices=FORM_ID_CHOICES
    )
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    date_received = models.DateField(null=True)
    date_filed = models.DateField(null=True)
    dupe = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='duplicate',
    )

    def __unicode__(self):
        return unicode(self.filing_id_raw)

    def get_absolute_url(self):
        return reverse('filing_detail', args=[str(self.pk)])

    @property
    def summary(self):
        try:
            return Summary.objects.get(
                filing_id_raw=self.filing_id_raw,
                amend_id=self.amend_id
            )
        except Summary.DoesNotExist:
            return None

    def is_amendment(self):
        return self.amend_id > 0


class Summary(models.Model):
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


class Expenditure(models.Model):
    '''
    This is a condensed version of the Raw CAL-ACCESS EXPN_CD table
    It leaves out a lot of the supporting information for the expense
    Like jurisdiction info, ballot initiative info,
    treasurer info, support/opposition info, etc.
    This just pulls in who got paid and how much
    And tries to prep the data for categorization by orgs and individuals
    Data comes from calaccess_raw.models.ExpnCd
    '''
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


class Contribution(models.Model):
    cycle = models.ForeignKey(Cycle)
    committee = models.ForeignKey(Committee)
    filing = models.ForeignKey(Filing)

    # Raw data fields
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=14,
        db_column='AMOUNT'
    )
    bakref_tid = models.CharField(max_length=20, blank=True)
    cmte_id = models.CharField(max_length=9, blank=True)
    ctrib_adr1 = models.CharField(max_length=55, blank=True)
    ctrib_adr2 = models.CharField(max_length=55, blank=True)
    ctrib_city = models.CharField(max_length=30, blank=True)
    ctrib_dscr = models.CharField(max_length=90, blank=True)
    ctrib_emp = models.CharField(max_length=200, blank=True)
    ctrib_namf = models.CharField(max_length=255, blank=True)
    ctrib_naml = models.CharField(max_length=200, )
    ctrib_nams = models.CharField(max_length=10, blank=True)
    ctrib_namt = models.CharField(max_length=10, blank=True)
    ctrib_occ = models.CharField(max_length=60, blank=True)
    ctrib_self = models.CharField(max_length=1, blank=True)
    ctrib_st = models.CharField(max_length=2, blank=True)
    ctrib_zip4 = models.CharField(max_length=10, blank=True)
    cum_oth = models.DecimalField(
        decimal_places=2, null=True, max_digits=14, blank=True)
    cum_ytd = models.DecimalField(
        decimal_places=2, null=True, max_digits=14, blank=True)
    date_thru = models.DateField(null=True, blank=True)
    entity_cd = models.CharField(max_length=3)
    form_type = models.CharField(max_length=9)
    intr_adr1 = models.CharField(max_length=55, blank=True)
    intr_adr2 = models.CharField(max_length=55, blank=True)
    intr_city = models.CharField(max_length=30, blank=True)
    intr_cmteid = models.CharField(max_length=9, blank=True)
    intr_emp = models.CharField(max_length=200, blank=True)
    intr_namf = models.CharField(max_length=255, blank=True)
    intr_naml = models.CharField(max_length=200, blank=True)
    intr_nams = models.CharField(max_length=10, blank=True)
    intr_namt = models.CharField(max_length=10, blank=True)
    intr_occ = models.CharField(max_length=60, blank=True)
    intr_self = models.CharField(max_length=1, blank=True)
    intr_st = models.CharField(max_length=2, blank=True)
    intr_zip4 = models.CharField(max_length=10, blank=True)
    line_item = models.IntegerField()
    memo_code = models.CharField(max_length=1, blank=True)
    memo_refno = models.CharField(max_length=20, blank=True)
    rcpt_date = models.DateField(null=True)
    rec_type = models.CharField(max_length=4)
    tran_id = models.CharField(max_length=20)
    tran_type = models.CharField(max_length=1, blank=True)
    xref_match = models.CharField(max_length=1, blank=True)
    xref_schnm = models.CharField(max_length=2, blank=True)

    # Derived fields
    raw_org_name = models.CharField(max_length=255)
    person_flag = models.BooleanField(default=False)
    org_id = models.IntegerField(null=True)
    individual_id = models.IntegerField(null=True)
    dupe = models.BooleanField(default=False)

    @property
    def raw(self):
        from calaccess_raw.models import RcptCd
        return RcptCd.objects.get(
            amend_id=self.amend_id,
            filing_id=self.filing_id,
            tran_id=self.tran_id,
            bakref_tid=self.bakref_tid
        )

    def get_absolute_url(self):
        return reverse('contribution_detail', args=[str(self.pk)])


class Stats(models.Model):
    '''
        Flexible model for housing aggregate stats
        Should be able to add any stat you like for
        a filer_type in the options list
        And record any notes about how it was calculated and why
        Should allow for speedier display of aggregate data
        If it end up not working, we can blow it up and try something else
    '''
    FILER_TYPE_CHOICES = (
        ('cand', 'Candidate'),
        ('pac', 'Political Action Committee'),
    )
    STAT_TYPE_CHOICES = (
        ('itemized_monetary_contributions', 'Itemized Monetary Contributions'),
        (
            'unitemized_monetary_contributions',
            'Unitemized Monetary Contributions'
        ),
        ('total_contributions', 'Total Contributions'),
        ('total_expenditures', 'Total Expenditures'),
        ('outstanding_debts', 'Outstanding Debt'),

    )
    filer_type = models.CharField(max_length=10, choices=FILER_TYPE_CHOICES)
    filer = models.ForeignKey(Filer)
    stat_type = models.CharField(max_length=50, choices=STAT_TYPE_CHOICES)
    notes = models.TextField(null=True, blank=True)
    int_year_span = models.IntegerField()  # years in operation eg. 10
    # string description eg. 2000 - 2010
    str_year_span = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=16, decimal_places=2)

    def __unicode__(self):
        return '%s-%s' % (self.filer_type, self.stat_type)


class FlatFile(models.Model):
    file_name = models.CharField(max_length=255)
    s3_file = models.FileField(upload_to='files')
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def _get_file_size(self):
        return size(self.s3_file.size)
    size = property(_get_file_size)

    def __unicode__(self):
        return self.file_name
