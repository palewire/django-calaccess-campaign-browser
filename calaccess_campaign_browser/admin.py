from django.contrib import admin
from calaccess_campaign_browser.models import (
    Committee,
    Filer,
    Summary,
    Expenditure,
    Contribution,
    FlatFile,
    Cycle,
    Filing,
)


class BaseAdmin(admin.ModelAdmin):
    save_on_top = True

    def get_readonly_fields(self, *args, **kwargs):
        return [f.name for f in self.model._meta.fields]


class FilingAdmin(BaseAdmin):
    list_display = (
        "filing_id_raw",
        "committee",
        "form_id",
        "cycle",
        "start_date",
        "end_date",
        "amend_id",
        "dupe",
    )
    list_filter = (
        "form_id",
        "dupe",
        "cycle",
    )
    search_fields = (
        "filing_id_raw",
    )


class FilerAdmin(BaseAdmin):
    list_display = (
        "filer_id",
        "name",
        "filer_type",
        "status",
        "effective_date",
        "xref_filer_id"
    )
    list_filter = (
        "filer_type",
        "status",
    )
    search_fields = (
        "name",
        "filer_id",
        "xref_filer_id"
    )
    date_hierarchy = "effective_date"


class CommitteeAdmin(BaseAdmin):
    list_display = (
        "filer_id_raw",
        "name",
        "filer",
        "committee_type",
    )
    list_filter = (
        "committee_type",
    )
    search_fields = (
        "name",
        "filer_id_raw",
    )


class CycleAdmin(BaseAdmin):
    list_display = ("name",)


class ContributionAdmin(BaseAdmin):
    list_display = (
        "id",
        "raw_org_name",
        "committee",
        "rcpt_date",
        "amount",
        "dupe"
    )
    list_filter = (
        "dupe",
    )
    search_fields = (
        "raw_org_name",
    )
    date_hierarchy = "rcpt_date"


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
        "id",
        "committee",
        "filing",
        "form_type",
        "total_contributions",
        "total_expenditures",
        "dupe"
    )
    list_filter = (
        "dupe",
        "form_type"
    )


admin.site.register(Committee, CommitteeAdmin)
admin.site.register(Filer, FilerAdmin)
admin.site.register(Cycle, CycleAdmin)
admin.site.register(Filing, FilingAdmin)
admin.site.register(Expenditure, ExpenditureAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(FlatFile)
admin.site.register(Summary, SummaryAdmin)
