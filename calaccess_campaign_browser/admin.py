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
)


class BaseAdmin(admin.ModelAdmin):
    save_on_top = True

    def get_readonly_fields(self, *args, **kwargs):
        return [f.name for f in self.model._meta.fields]


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


class CommitteeAdmin(BaseAdmin):
    list_display = (
        "filer_id_raw",
        "short_name",
        "filer_short_name",
        "committee_type",
        "cycle",
        "party",
        "status",
        "effective_date",
    )
    list_filter = (
        "committee_type",
        "election_type",
        "category_type",
        "party",
        "status",
        "cycle",
    )
    search_fields = (
        "name",
        "filer_id_raw",
        "xref_filer_id"
    )
    date_hierarchy = "effective_date"


class CycleAdmin(BaseAdmin):
    list_display = ("name",)


class FilingPeriodAdmin(BaseAdmin):
    list_display = (
        "period_id", "name", "start_date", "end_date", "deadline",
    )
    search_fields = (
        "period_id",
    )


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


admin.site.register(Committee, CommitteeAdmin)
admin.site.register(Filer, FilerAdmin)
admin.site.register(Cycle, CycleAdmin)
admin.site.register(FilingPeriod, FilingPeriodAdmin)
admin.site.register(Filing, FilingAdmin)
admin.site.register(Expenditure, ExpenditureAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(Summary, SummaryAdmin)
