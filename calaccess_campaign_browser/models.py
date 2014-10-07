from django.db import models
from hurry.filesize import size
from .managers import RealManager
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict
from .utils.models import AllCapsNameMixin, BaseModel
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
    RACE_CHOICES = (
        ('0', 'N/A'),
        ('30059', 'APPELLATE COURT JUDGE'),
        ('30058', 'PUBLIC EMPLOYEES RETIREMENT BOARD'),
        ('30057', 'SUPREME COURT JUDGE'),
        ('30056', 'CITY PROSECUTOR'),
        ('30055', 'MEASURE'),
        ('30054', 'DISTRICT ATTORNEY/PUBLIC DEFENDER'),
        ('30053', 'SUPERIOR COURT JUDGE'),
        ('30052', 'BOARD OF SUPERVISORS'),
        ('30051', 'COMMUNITY PLANNING GROUP'),
        ('30050', 'WATER BOARD'),
        ('30049', 'IRRIGATION'),
        ('30048', 'BOARD OF TRUSTEES'),
        ('30047', 'BART BOARD DIRECTOR'),
        ('30046', 'COLLEGE BOARD'),
        ('30045', 'BOARD OF DIRECTORS'),
        ('30044', 'BOARD OF EDUCATION'),
        ('30043', 'CENTRAL COMMITTEE'),
        ('30042', 'CHIEF OF POLICE'),
        ('30041', 'POLICE CHIEF'),
        ('30040', 'COMMUNITY COLLEGE BOARD'),
        ('30039', 'DIRECTOR OF ZONE 7'),
        ('30038', 'DIRECTOR'),
        ('30037', 'REPUBLICAN COUNTY CENTRAL COMMITTEE'),
        ('30036', 'COMMISSIONER'),
        ('30035', 'CITY COUNCIL'),
        ('30034', 'CITY TREASURER'),
        ('30033', 'ASSESSOR'),
        ('30032', 'TOWN COUNCIL'),
        ('30031', 'DEMOCRATIC COUNTY CENTRAL COMMITTEE'),
        ('30030', 'CITY ATTORNEY'),
        ('30029', 'MAYOR'),
        ('30028', 'AUDITOR'),
        ('30027', 'COUNTY CLERK'),
        ('30026', 'DISTRICT ATTORNEY'),
        ('30025', 'HARBOR COMMISSIONER'),
        ('30024', 'SCHOOL BOARD'),
        ('30023', 'CITY CLERK'),
        ('30022', 'MARSHALL'),
        ('30021', 'CORONER'),
        ('30020', 'SHERIFF'),
        ('30019', 'SUPERVISOR'),
        ('30018', 'TRUSTEE'),
        ('30017', 'TAX COLLECTOR'),
        ('30016', 'BOARD MEMBER'),
        ('30015', 'JUDGE'),
        ('30014', 'INSURANCE COMMISSIONER'),
        ('30013', 'ASSEMBLY'),
        ('30012', 'STATE SENATE'),
        ('30011', 'CITY CONTROLLER'),
        ('30010', 'OXNARD HARBOR COMMISSIONER'),
        ('30009', 'MEMBER BOARD OF EQUALIZATION'),
        ('30008', 'SUPERINTENDENT OF PUBLIC INSTRUCTION'),
        ('30007', 'ATTORNEY GENERAL'),
        ('30006', 'TREASURER'),
        ('30005', 'CONTROLLER'),
        ('30004', 'SECRETARY OF STATE'),
        ('30003', 'LIEUTENANT GOVERNOR'),
        ('30002', 'GOVERNOR'),
        ('30001', 'PRESIDENT'),
        ('50085', 'Weed Recreation Board Member'),
        ('50084', 'Trustee'),
        ('50083', 'Treasurer/Tax Collector/Recorder'),
        ('50082', 'Treasurer/Tax Collector/Public Administrator/County Clerk'),
        ('50081', 'Treasurer/Tax Collector/Public Administrator'),
        ('50080', 'Treasurer/Tax Collector/Clerk'),
        ('50079', 'Treasurer/Tax Collector'),
        ('50078', 'Treasurer'),
        ('50077', 'Town Council'),
        ('50076', 'Tax Collector'),
        ('50075', 'Supt Of Schools'),
        ('50074', 'Supervisor'),
        ('50073', 'Superintendent'),
        ('50072', 'Solana Beach'),
        ('50071', 'Sheriff/Coroner/Public Administrator'),
        ('50070', 'Sheriff/Coroner/Marshall'),
        ('50069', 'Sheriff/Coroner'),
        ('50068', 'Sheriff'),
        ('50067', 'Senator'),
        ('50066', 'Secretary Of State'),
        ('50065', 'School Board'),
        ('50064', 'Sanger'),
        ('50063', 'San Francisco Dccc'),
        ('50062', 'Republican Central Committee'),
        ('50061', 'Rent Stabilization Board'),
        ('50060', 'Public Administrator/Guardian'),
        ('50059', 'Public Administrator'),
        ('50058', 'Placentia'),
        ('50057', 'N/A'),
        ('50056', 'Mayor'),
        ('50055', 'Lieutenant Governor'),
        ('50054', 'Legislature'),
        ('50053', 'Justice'),
        ('50052', 'Judge'),
        ('50051', 'Irrigation Dist'),
        ('50050', 'Ic'),
        ('50049', 'Harbor Commissioner'),
        ('50048', 'Governor'),
        ('50047', 'Gccc'),
        ('50046', 'District Attorney/Public Administrator'),
        ('50045', 'District Attorney'),
        ('50044', 'Director'),
        ('50043', 'Democratic County Central Committee'),
        ('50042', 'County Clerk/Recorder/Public Admin'),
        ('50041', 'County Clerk/Recorder/Assessor'),
        ('50040', 'County Clerk/Recorder'),
        ('50039', 'County Clerk/Auditor/Controller'),
        ('50038', 'County Clerk/Auditor'),
        ('50037', 'County Clerk'),
        ('50036', 'Council Member'),
        ('50035', 'Costa Mesa'),
        ('50034', 'Controller'),
        ('50033', 'Commissioner'),
        ('50032', 'Clerk/Recorder/Registrar'),
        ('50031', 'Clerk/Recorder/Registar'),
        ('50030', 'Clerk/Recorder'),
        ('50029', 'Clerk/Record/Public Admin'),
        ('50028', 'Clerk/Auditor'),
        ('50027', 'City Treasurer'),
        ('50026', 'City Prosecutor'),
        ('50025', 'City Of South El Monte'),
        ('50024', 'City Of Los Angeles'),
        ('50023', 'City Council'),
        ('50022', 'City Clerk'),
        ('50021', 'City Auditor'),
        ('50020', 'City Attorney'),
        ('50019', 'City'),
        ('50018', 'Chief Justice'),
        ('50017', 'Boe'),
        ('50016', 'Board Of Supervisor'),
        ('50015', 'Board Of Director'),
        ('50014', 'Board Member'),
        ('50013', 'Auditor/Recorder'),
        ('50012', 'Auditor/Controller/Treasurer/Tax Collector'),
        ('50011', 'Auditor/Controller/Recorder'),
        ('50010', 'Auditor/Controller/Clerk/Recorder'),
        ('50009', 'Auditor/Controller'),
        ('50008', 'Auditor'),
        ('50007', 'Associate Justice'),
        ('50006', 'Assessor/Recorder'),
        ('50005', 'Assessor/County Clerk/Recorder'),
        ('50004', 'Assessor/Clerk/Recorder'),
        ('50003', 'Assessor'),
        ('50002', 'Assembly'),
        ('50001', 'Ag'),
    )
    race = models.CharField(
        max_length=255,
        null=True,
        choices=RACE_CHOICES
    )
    CATEGORY_CHOICES = (
        ('40001', 'Jointly controlled'),
        ('40002', 'Controlled'),
        ('40003', 'Caucus committee'),
        ('40004', 'Unknown'),
        ('0', 'N/A'),
    )
    category = models.CharField(
        max_length=255,
        null=True,
        choices=CATEGORY_CHOICES
    )
    CATEGORY_TYPE_CHOICES = (
        ('40501', 'LOCAL'),
        ('40502', 'STATE'),
        ('40503', 'COUNTY'),
        ('40504', 'MULTI-COUNTY'),
        ('40505', 'CITY'),
        ('40506', 'FEDERAL'),
        ('40507', 'SUPERIOR COURT JUDGE'),
        ('0', 'N/A'),
    )
    category_type = models.CharField(
        max_length=255,
        null=True,
        choices=CATEGORY_TYPE_CHOICES
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
        return Filing.real.filter(committee=self).select_related("cycle")

    @property
    def total_contributions(self):
        summaries = [f.summary for f in self.real_filings]
        summaries = [s for s in summaries if s]
        return sum([
            s.total_contributions for s in summaries if s.total_contributions
        ])

    @property
    def total_contributions_by_year(self):
        d = {}
        for f in self.real_filings:
            if not f.summary:
                continue
            if not f.summary.total_contributions:
                continue
            try:
                d[f.period.start_date.year] += f.summary.total_contributions
            except KeyError:
                d[f.period.start_date.year] = f.summary.total_contributions
        return sorted(d.items(), key=lambda x:x[0], reverse=True)

    @property
    def total_contributions_by_cycle(self):
        d = {}
        for f in self.real_filings:
            if not f.summary:
                continue
            if not f.summary.total_contributions:
                continue
            try:
                d[f.cycle.name] += f.summary.total_contributions
            except KeyError:
                d[f.cycle.name] = f.summary.total_contributions
        return sorted(d.items(), key=lambda x:x[0], reverse=True)

    @property
    def total_expenditures(self):
        summaries = [f.summary for f in self.real_filings]
        summaries = [s for s in summaries if s]
        return sum([
            s.total_expenditures for s in summaries if s.total_expenditures
        ])

    @property
    def total_expenditures_by_cycle(self):
        d = {}
        for f in self.real_filings:
            if not f.summary:
                continue
            if not f.summary.total_expenditures:
                continue
            try:
                d[f.cycle.name] += f.summary.total_expenditures
            except KeyError:
                d[f.cycle.name] = f.summary.total_expenditures
        return sorted(d.items(), key=lambda x:x[0], reverse=True)

    @property
    def total_expenditures_by_year(self):
        d = {}
        for f in self.real_filings:
            if not f.summary:
                continue
            if not f.summary.total_expenditures:
                continue
            try:
                d[f.period.start_date.year] += f.summary.total_expenditures
            except KeyError:
                d[f.period.start_date.year] = f.summary.total_expenditures
        return sorted(d.items(), key=lambda x:x[0], reverse=True)


class Cycle(BaseModel):
    name = models.IntegerField(db_index=True)

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
            dateformat(self.start_date, "%Y-%m-%d"),
            dateformat(self.end_date, "%m-%d"),
        )


class Filing(models.Model):
    cycle = models.ForeignKey(Cycle)
    committee = models.ForeignKey(Committee)
    filing_id_raw = models.IntegerField('filing ID', db_index=True)
    amend_id = models.IntegerField('amendment', db_index=True)
    FORM_TYPE_CHOICES = (
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
    real = RealManager()

    def __unicode__(self):
        return unicode(self.filing_id_raw)

    def get_absolute_url(self):
        return reverse('filing_detail', args=[str(self.pk)])

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

    def is_amendment(self):
        return self.amend_id > 0


class Summary(BaseModel):
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
    real = RealManager()

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
