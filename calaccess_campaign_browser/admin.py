from django.contrib import admin
from calaccess_campaign_browser.models import (
    Committee,
    Filer,
    Summary,
    Expenditure,
    Contribution,
    FlatFile
)

class BaseAdmin(admin.ModelAdmin):
    save_on_top = True

    def get_readonly_fields(self, *args, **kwargs):
        return [f.name for f in self.model._meta.fields]


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


admin.site.register(Committee, CommitteeAdmin)
admin.site.register(Filer, FilerAdmin)
admin.site.register(Expenditure)
admin.site.register(Contribution)
admin.site.register(FlatFile)
admin.site.register(Summary)
