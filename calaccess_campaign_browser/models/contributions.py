from django.db import models
from calaccess_campaign_browser import managers
from django.utils.datastructures import SortedDict
from calaccess_campaign_browser.utils.models import BaseModel


class Contribution(BaseModel):
    """
    Who gave and how much.
    """
    cycle = models.ForeignKey('Cycle')
    committee = models.ForeignKey(
        'Committee',
        related_name="contributions_to"
    )
    filing = models.ForeignKey('Filing')

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
        blank=True,
        default='',
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
        'Committee',
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

    class Meta:
        app_label = 'calaccess_campaign_browser'

    @models.permalink
    def get_absolute_url(self):
        return ('contribution_detail', [str(self.pk)])

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
