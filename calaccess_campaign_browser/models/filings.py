import json
from django.db import models
from django.db.models import Sum
from calaccess_campaign_browser import managers
from calaccess_campaign_browser.utils.models import BaseModel
from calaccess_campaign_browser.models import Contribution, Expenditure
from calaccess_campaign_browser.templatetags.calaccesscampaignbrowser import (
    jsonify
)


class Cycle(BaseModel):
    name = models.IntegerField(db_index=True, primary_key=True)

    class Meta:
        ordering = ("-name",)
        app_label = 'calaccess_campaign_browser'

    def __unicode__(self):
        return unicode(self.name)


class Filing(models.Model):
    cycle = models.ForeignKey('Cycle')
    committee = models.ForeignKey('Committee')
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

    class Meta:
        app_label = 'calaccess_campaign_browser'

    def __unicode__(self):
        return unicode(self.filing_id_raw)

    @models.permalink
    def get_absolute_url(self):
        return ('filing_detail', [str(self.pk)])

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
        app_label = 'calaccess_campaign_browser'

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
