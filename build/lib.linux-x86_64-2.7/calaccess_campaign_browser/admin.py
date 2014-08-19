from django.contrib import admin
from calaccess_campaign_browser.models import (
    Committee,
    Filer,
    Summary,
    Expenditure,
    Contribution,
    FlatFile
)

admin.site.register(Committee)
admin.site.register(Filer)
admin.site.register(Expenditure)
admin.site.register(Contribution)
admin.site.register(FlatFile)
admin.site.register(Summary)
