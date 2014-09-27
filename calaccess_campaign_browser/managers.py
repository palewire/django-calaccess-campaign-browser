from django.db import models


class RealManager(models.Manager):
    """
    Only returns records that are not duplicates
    and should be treated for lists and counts as "real."
    """
    def get_queryset(self):
        qs = super(RealManager, self).get_queryset()
        return qs.exclude(is_duplicate=True)
