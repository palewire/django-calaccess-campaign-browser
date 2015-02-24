from datetime import datetime
from django.test import TestCase
from calaccess_campaign_browser import models


class ModelTest(TestCase):
    """
    Create model objects and try out their attributes.
    """
    def test_filer(self):
        obj = models.Filer.objects.create(
            name="FooPAC",
            filer_id_raw=1,
            xref_filer_id=1,
            filer_type="PAC",
            party='0',
            status='A',
            effective_date=datetime.now()
        )
        obj.__unicode__()
        obj.slug
        obj.real_filings
        obj.total_contributions
        obj.meta()
        obj.klass()
        obj.doc()
        obj.to_dict()
        obj.to_json()
        obj.short_name
        obj.clean_name

    def test_committee(self):
        pass

    def test_cycle(self):
        pass

    def test_filingperiod(self):
        pass

    def test_filing(self):
        pass

    def test_summary(self):
        pass

    def test_contribution(self):
        pass

    def test_office(self):
        pass

    def test_candidate(self):
        pass

    def test_proposition(self):
        pass

    def test_propositionfiler(self):
        pass
