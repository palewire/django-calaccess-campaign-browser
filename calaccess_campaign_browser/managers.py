from django.db import models


class BaseRealManager(models.Manager):
    """
    Base class with common methods used by managers that exclude duplicate
    records from data models.
    """
    def get_queryset(self):
        qs = super(BaseRealManager, self).get_queryset()
        return qs.exclude(is_duplicate=True)

    def get_committee(self, obj_or_id):
        """
        Returns a Committee model object whether you submit the primary key
        from our database or the CAL-ACCESS filing id.

        If a Committee object is submitted it is returns as is.
        """
        from .models import Committee

        # Pull the committee object
        if isinstance(obj_or_id, Committee):
            cmte = obj_or_id
        elif isinstance(obj_or_id, int):
            try:
                cmte = Committee.objects.get(id=obj_or_id)
            except Committee.DoesNotExist:
                cmte = Committee.objects.get(filing_id_raw=obj_or_id)
        else:
            raise ValueError("You must submit a committee object or ID")
        return cmte


class RealFilingManager(BaseRealManager):
    """
    Only returns records that are not duplicates
    and should be treated for lists and counts as "real."
    """
    def by_committee(self, obj_or_id):
        """
        Returns the "real" or valid filings for a particular committee.
        """
        cmte = self.get_committee(obj_or_id)

        # Filer to only filings by this committee
        qs = self.get_queryset().filter(committee=cmte)

        # Get most recent end date for quarterly filings
        try:
            most_recent_quarterly = qs.filter(
                form_type__in=['F450', 'F460']
            ).order_by("-end_date")[0]
        except (qs.model.DoesNotExist, IndexError):
            # If there are none, just return everything
            return qs

        # Exclude all F497 late filings that come before that date
        qs = qs.exclude(
            form_type='F497',
            start_date__lte=most_recent_quarterly.end_date
        )

        # Retun the result
        return qs


class RealContributionManager(BaseRealManager):
    """
    Only returns records that are not duplicates.
    """
    def by_committee_to(self, obj_or_id):
        """
        Returns the "real" or valid contributions received by
        a particular committee.
        """
        from .models import Filing

        # Pull the committee object
        cmte = self.get_committee(obj_or_id)

        # Get a list of the valid filings for this committee
        filing_list = Filing.real.by_committee(cmte)

        # Filer to only contributions from real filings by this committee
        qs = self.get_queryset().filter(
            committee=cmte,
            filing__in=filing_list
        )

        # Retun the result
        return qs

    def by_committee_from(self, obj_or_id):
        """
        Returns the "real" or valid contributions made by
        a particular committee.
        """
        from .models import Filing

        # Pull the committee object
        cmte = self.get_committee(obj_or_id)

        # Get a list of the valid filings for this committee
        filing_list = Filing.real.by_committee(cmte)

        # Filer to only contributions from real filings by this committee
        qs = self.get_queryset().filter(
            contributor_committee=cmte,
            filing__in=filing_list
        )

        # Retun the result
        return qs


class RealExpenditureManager(models.Manager):
    """
    Only returns records that are not duplicates.
    """
    def get_queryset(self):
        qs = super(RealExpenditureManager, self).get_queryset()
        return qs.exclude(dupe=True)
