from django.db import models
from calaccess_campaign_browser import managers
from calaccess_campaign_browser.utils.models import BaseModel


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
    cycle = models.ForeignKey('Cycle')
    committee = models.ForeignKey('Committee')
    filing = models.ForeignKey('Filing')

    # Raw data fields
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    bakref_tid = models.CharField(max_length=50L, blank=True)
    cmte_id = models.CharField(max_length=9L, blank=True)
    cum_ytd = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    entity_cd = models.CharField(max_length=5L, blank=True)
    expn_chkno = models.CharField(max_length=20L, blank=True)
    expn_code = models.CharField(
        max_length=3L,
        blank=True,
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

    class Meta:
        app_label = 'calaccess_campaign_browser'

    @models.permalink
    def get_absolute_url(self):
        return ('expenditure_detail', [str(self.pk)])

    @property
    def raw(self):
        from calaccess_raw.models import ExpnCd
        return ExpnCd.objects.get(
            amend_id=self.amend_id,
            filing_id=self.filing_id,
            tran_id=self.tran_id,
            bakref_tid=self.bakref_tid
        )
