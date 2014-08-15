from django.contrib import admin
from campaign_finance.models import (
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
