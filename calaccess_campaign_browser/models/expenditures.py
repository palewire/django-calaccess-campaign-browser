from django.db import models
from django.utils.datastructures import SortedDict

from calaccess_campaign_browser import managers
from calaccess_campaign_browser.utils.models import BaseModel


class Expenditure(BaseModel):
    """
    Who got paid and how much.
    """
    cycle = models.ForeignKey('Cycle')
    committee = models.ForeignKey(
        'Committee',
        related_name='expenditures_to'
    )
    filing = models.ForeignKey('Filing')

    # CAL-ACCESS ids
    filing_id_raw = models.IntegerField(db_index=True, null=True)
    transaction_id = models.CharField(
        'transaction ID',
        max_length=20,
        db_index=True,
        blank=True,
        null=True
    )
    amend_id = models.IntegerField('amendment', db_index=True)
    backreference_transaction_id = models.CharField(
        'backreference transaction ID',
        max_length=50,
        db_index=True
    )
    is_crossreference = models.CharField(max_length=1, blank=True)
    crossreference_schedule = models.CharField(max_length=2, blank=True)

    # Basics about expenditure
    is_duplicate = models.BooleanField(default=False)

    date_received = models.DateField(null=True)
    expenditure_description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2)

    # About the candidate
    candidate_full_name = models.CharField(max_length=255)
    candidate_is_person = models.BooleanField(default=False)
    candidate_committee = models.ForeignKey(
        'Committee',
        null=True,
        related_name="expenditures_from"
    )
    candidate_prefix = models.CharField(max_length=10, blank=True)
    candidate_first_name = models.CharField(max_length=255, blank=True)
    candidate_last_name = models.CharField(max_length=200, blank=True)
    candidate_suffix = models.CharField(max_length=10, blank=True)

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
    candidate_expense_code = models.CharField(
        max_length=3,
        blank=True,
        choices=EXPENDITURE_CODE_CHOICES
    )
    ENTITY_CD_CHOICES = (
        ('COM', 'Recipient Committee'),
        ('RCP', 'Recipient Committee'),
        ('IND', 'Individual'),
        ('OTH', 'Other'),
        ('PTY', 'PTY - Unknown'),
        ('SCC', 'SCC 0 Unknown'),
        ('BNM', 'BNM - Unknown'),
        ('CAO', 'CAO - Unknown'),
        ('OFF', 'OFF - Unknown'),
        ('PTH', 'PTH - Unknown'),
        ('RFD', 'RFD - Unknown'),
        ('MBR', 'MBR - Unknown'),
        ('0', '0 - Unknown'),
    )
    candidate_entity_type = models.CharField(
        max_length=3,
        blank=True,
        help_text="The type of entity that made that expenditure",
        choices=ENTITY_CD_CHOICES
    )

    # About the payee
    payee_prefix = models.CharField(max_length=10, blank=True)
    payee_first_name = models.CharField(max_length=255, blank=True)
    payee_last_name = models.CharField(max_length=200, blank=True)
    payee_suffix = models.CharField(max_length=10, blank=True)
    payee_city = models.CharField(max_length=30, blank=True)
    payee_state = models.CharField(max_length=2, blank=True)
    payee_zipcode = models.CharField(max_length=10, blank=True)
    payee_committee_id = models.CharField(max_length=9, blank=True)
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
            filing_id=self.filing.filing_id_raw,
            tran_id=self.transaction_id,
            bakref_tid=self.backreference_transaction_id
        )

    @property
    def candidate_dict(self):
        d = SortedDict({})
        for k, v in self.to_dict().items():
            if k.startswith("candidate"):
                d[k.replace("candidate ", "")] = v
        return d

    @property
    def payee_dict(self):
        d = SortedDict({})
        for k, v in self.to_dict().items():
            if k.startswith("payee"):
                d[k.replace("payee ", "")] = v
        return d
