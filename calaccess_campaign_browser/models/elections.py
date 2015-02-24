from django.db import models
from calaccess_campaign_browser.utils.models import BaseModel


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
        app_label = 'calaccess_campaign_browser'

    def __unicode__(self):
        return self.name

    @property
    def name(self):
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
        app_label = 'calaccess_campaign_browser'

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
    election = models.ForeignKey('Election')
    office = models.ForeignKey('Office')
    filer = models.ForeignKey('Filer')

    class Meta:
        ordering = ("election", "office", "filer")
        app_label = 'calaccess_campaign_browser'

    def __unicode__(self):
        return u'%s: %s [%s]' % (self.filer, self.office, self.election)

    @property
    def election_year(self):
        return self.election.year

    @property
    def election_type(self):
        return self.election.get_election_type_display()


class Proposition(BaseModel):
    """
    A proposition or ballot measure decided by voters.
    """
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True)
    id_raw = models.IntegerField(db_index=True)
    election = models.ForeignKey('Election', null=True, default=None)
    filers = models.ManyToManyField('Filer', through='PropositionFiler')

    class Meta:
        ordering = ("election", "name")
        app_label = 'calaccess_campaign_browser'

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
    proposition = models.ForeignKey('Proposition')
    filer = models.ForeignKey('Filer')
    position = models.CharField(
        choices=POSITION_CHOICES,
        max_length=50
    )

    class Meta:
        app_label = 'calaccess_campaign_browser'

    def __unicode__(self):
        return '%s %s' % (self.proposition, self.filer)
