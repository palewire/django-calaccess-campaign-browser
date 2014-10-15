from django.db import models


class RealFilingManager(models.Manager):
    """
    Only returns records that are not duplicates
    and should be treated for lists and counts as "real."
    """
    def get_queryset(self):
        qs = super(RealFilingManager, self).get_queryset()
        return qs.exclude(is_duplicate=True)

    def by_committee(self, obj_or_id):
        """
        Returns the "real" or valid filings for a particular committee.
        """
        from .models import Committee

        # Pull the committee object
        if isinstance(obj_or_id, int):
            try:
                cmte = Committee.objects.get(id=obj_or_id)
            except Committee.DoesNotExist:
                cmte = Committee.objects.get(filing_id_raw=obj_or_id)
        elif isinstance(obj_or_id, Committee):
            cmte = obj_or_id
        else:
            raise ValueError("You must submit a committee object or ID")

        # Filer to only filings by this committee
        qs = self.get_queryset().filter(committee=cmte)

        # Get most recent end date for quarterly filings
        try:
            most_recent_quarterly = qs.filter(
                form_type__in=['F450', 'F460']
            ).order_by("-period__end_date")[0]
        except qs.model.DoesNotExist:
            # If there are none, just return everything
            return qs

        # Exclude all F497 late filings that come before that date
        qs = qs.exclude(
            form_type='F497', 
            period__start_date__lte=most_recent_quarterly.period.end_date
        )

        # Retun the result
        return qs


class RealContributionManager(models.Manager):
    """
    Only returns records that are not duplicates.
    """
    def get_queryset(self):
        qs = super(RealContributionManager, self).get_queryset()
        return qs.exclude(is_duplicate=True)


class RealExpenditureManager(models.Manager):
    """
    Only returns records that are not duplicates.
    """
    def get_queryset(self):
        qs = super(RealExpenditureManager, self).get_queryset()
        return qs.exclude(dupe=True)
