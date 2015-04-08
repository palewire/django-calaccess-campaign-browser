from csvkit import CSVKitWriter
from django.db import connection
from calaccess_campaign_browser import models
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = 'Export candidates scraped from the state site'

    def handle(self, *args, **options):
        self.cursor = connection.cursor()
        sql = """
        SELECT DISTINCT
            o.name,
            o.seat,
            f.filer_id_raw,
            f.xref_filer_id,
            f.name,
            f.party
        FROM %(candidate)s as c
        INNER JOIN %(office)s as o
        ON c.office_id = o.id
        INNER JOIN %(filer)s as f
        ON c.filer_id = f.id
        """ % dict(
            candidate=models.Candidate._meta.db_table,
            office=models.Office._meta.db_table,
            filer=models.Filer._meta.db_table,
        )
        self.cursor.execute(sql)
        writer = CSVKitWriter(open("./candidates.csv", 'wb'))
        writer.writerow([
            'office_name',
            'office_seat',
            'filer_id',
            'xref_filer_id',
            'name',
            'party'
        ])
        writer.writerows(self.cursor.fetchall())
