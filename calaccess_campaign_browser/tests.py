from datetime import datetime
from django.test import TestCase
from calaccess_campaign_browser import models


class ModelTest(TestCase):
    """
    Create model objects and try out their attributes.
    """
    def test_models(self):
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
        filer = models.Filer.objects.create(
            name="Foo Nixon",
            filer_id_raw=1,
            xref_filer_id=1,
            filer_type="cand",
            party='16002',
            status='A',
            effective_date=datetime.now()
        )
        committee = models.Committee.objects.create(
            name='Nixon for Governor',
            filer=filer,
            filer_id_raw=filer.filer_id_raw,
            xref_filer_id=filer.xref_filer_id,
            committee_type=filer.filer_type,
            party=filer.party,
            status='Y',
            level_of_government='40502',
            effective_date=filer.effective_date,
        )
        committee.__unicode__()

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
