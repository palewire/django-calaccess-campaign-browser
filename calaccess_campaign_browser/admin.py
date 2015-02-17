from django.contrib import admin
from calaccess_campaign_browser.models import (
    Committee,
    Filer,
    Summary,
    Expenditure,
    Contribution,
    Cycle,
    FilingPeriod,
    Filing,
    Election,
    Office,
    Candidate,
    Proposition,
    PropositionFiler,
)


class BaseAdmin(admin.ModelAdmin):
    save_on_top = True

    def get_readonly_fields(self, *args, **kwargs):
        return [f.name for f in self.model._meta.fields]


@admin.register(Filing)
class FilingAdmin(BaseAdmin):
    list_display = (
        "filing_id_raw",
        "committee_short_name",
        "form_type",
        "cycle",
        "period",
        "amend_id",
        "is_duplicate",
    )
    list_filter = (
        "form_type",
        "is_duplicate",
        "cycle",
    )
    search_fields = (
        "filing_id_raw",
    )


@admin.register(Filer)
class FilerAdmin(BaseAdmin):
    list_display = (
        "filer_id_raw",
        "name",
        "filer_type",
        "party",
        "status",
        "effective_date",
        "xref_filer_id"
    )
    list_filter = (
        "filer_type",
        "party",
        "status",
    )
    search_fields = (
        "name",
        "filer_id_raw",
        "xref_filer_id"
    )
    date_hierarchy = "effective_date"


@admin.register(Committee)
class CommitteeAdmin(BaseAdmin):
    list_display = (
        "filer_id_raw",
        "short_name",
        "filer_short_name",
        "level_of_government",
        "party",
        "status",
        "effective_date",
    )
    list_filter = (
        "committee_type",
        "level_of_government",
        "party",
        "status",
    )
    search_fields = (
        "name",
        "filer_id_raw",
        "xref_filer_id"
    )
    date_hierarchy = "effective_date"


@admin.register(Cycle)
class CycleAdmin(BaseAdmin):
    list_display = ("name",)


@admin.register(FilingPeriod)
class FilingPeriodAdmin(BaseAdmin):
    list_display = (
        "period_id", "name", "start_date", "end_date", "deadline",
    )
    search_fields = (
        "period_id",
    )


@admin.register(Contribution)
class ContributionAdmin(BaseAdmin):
    list_display = (
        "id",
        "contributor_full_name",
        "committee",
        "date_received",
        "amount",
        "is_duplicate"
    )
    list_filter = (
        "is_duplicate",
    )
    search_fields = (
        "contributor_full_name",
    )
    date_hierarchy = "date_received"


@admin.register(Expenditure)
class ExpenditureAdmin(BaseAdmin):
    list_display = (
        "id",
        "name",
        "raw_org_name",
        "committee",
        "expn_date",
        "dupe",
    )
    list_filter = (
        "dupe",
    )
    search_fields = (
        "name",
        "raw_org_name",
    )
    date_hierarchy = "expn_date"


@admin.register(Summary)
class SummaryAdmin(BaseAdmin):
    list_display = (
        "filing_id_raw",
        "amend_id",
        "committee",
        "filing",
        "total_contributions",
        "total_expenditures",
    )
    search_fields = (
        "filing_id_raw",
        "amend_id",
    )


@admin.register(Election)
class ElectionAdmin(BaseAdmin):
    list_display = (
        "id_raw",
        "year",
        "election_type",
        "date",
        "office_count",
        "candidate_count",
    )
    list_filter = (
        "year",
        "election_type",
    )


@admin.register(Office)
class OfficeAdmin(BaseAdmin):
    list_display = (
        "__unicode__",
        "election_count",
        "candidate_count",
    )
    list_filter = (
        "name",
    )
    search_fields = (
        "name",
        "seat",
    )
    list_per_page = 200


@admin.register(Candidate)
class CandidateAdmin(BaseAdmin):
    list_display = (
        "filer", "election_year", "election_name", "office"
    )
    list_filter = (
        "election",
    )
    search_fields = (
        "filer__name",
    )


@admin.register(Proposition)
class PropositionAdmin(BaseAdmin):
    list_display = (
        "name",
        "short_description",
        "id_raw",
        "election",
    )
    list_filter = (
        "election",
    )
    search_fields = (
        "name",
        "short_description",
    )
    list_per_page = 500


@admin.register(PropositionFiler)
class PropositionFilerAdmin(BaseAdmin):
    list_display = (
        "proposition",
        "filer",
        "position",
    )
