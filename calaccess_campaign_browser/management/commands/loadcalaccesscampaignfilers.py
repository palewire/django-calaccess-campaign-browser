from django.db import connection
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.models import Filer, Committee


class Command(BaseCommand):

    def handle(self, *args, **options):
        c = connection.cursor()
        c.execute('DELETE FROM %s' % Committee._meta.db_table)
        c.execute('DELETE FROM %s' % Filer._meta.db_table)
        self.load_candidate_filers()
        self.load_candidate_committees()
        self.load_pac_filers()
        self.load_pac_committees()

    def load_candidate_filers(self):
        """
        Load all of the distinct candidate filers into the Filing table.
        """
        print "- Extracting candidates and loading into Filer model"
        c = connection.cursor()
        sql = """
        INSERT INTO %s (
            filer_id,
            status,
            effective_date,
            xref_filer_id,
            filer_type,
            name
        )
        SELECT
         FILERNAME_CD.`FILER_ID` as filer_id,
         FILERNAME_CD.`STATUS` as status,
         FILERNAME_CD.`EFFECT_DT` as effective_date,
         FILERNAME_CD.`XREF_FILER_ID` as xref_filer_id,
        -- Marking these as candidate record in our target data table
         'cand' as filer_type,
        -- Combining and cleaning up the name data from the source
         REPLACE(TRIM(
            CONCAT(`NAMT`, " ", `NAMF`, " ", `NAML`, " ", `NAMS`)
         ), '  ', ' ') as name
        FROM FILERNAME_CD
        INNER JOIN (
            -- Joining against a subquery that returns the last record
            -- in the source table because there are duplicates and we
            -- do not know of any logical way to better infer the most
            -- recent or complete record.
            SELECT FILER_ID, MAX(`id`) as `id`
            FROM FILERNAME_CD
            -- This filter limits the source data to only candidate filers
            WHERE `FILER_TYPE` = 'CANDIDATE/OFFICEHOLDER'
            GROUP BY 1
        ) as max
        ON FILERNAME_CD.`id` = max.`id`
        """ % (
            Filer._meta.db_table,
        )
        c.execute(sql)

    def load_candidate_committees(self):
        """
        Connect candidate filers to committees that are directly linked to
        their campaigns and then load those committees into a consolidated
        table.
        """
        print "- Loading committees linked to candidate filers into \
Committee model"
        c = connection.cursor()
        sql = """
        INSERT INTO %s (
            filer_id,
            filer_id_raw,
            name,
            committee_type
        )
        SELECT
            cand2cmte.`candidate_filer_pk` as filer_id,
            distinct_filers.`filer_id` as filer_id_raw,
            distinct_filers.`name` as name,
            'cand' as committee_type
        FROM (
            -- Two queries that join together via a UNION to return
            -- the corresponding committee filer ids that are linked
            -- to the candidate filer records from either direction (ie A or B)
            SELECT
                f.`id` as candidate_filer_pk,
                f.`FILER_ID` as candidate_filer_id,
                committee_filer_id_a.`FILER_ID_A` as committee_filer_id
            FROM calaccess_campaign_browser_filer f
            INNER JOIN (
                SELECT DISTINCT `FILER_ID_A`, `FILER_ID_B`
                FROM FILER_LINKS_CD
                WHERE LINK_TYPE = '12011'
                AND `FILER_ID_A` IS NOT NULL
            ) as committee_filer_id_a
            ON f.`FILER_ID` = committee_filer_id_a.`FILER_ID_B`
            AND f.`FILER_ID` <> committee_filer_id_a.`FILER_ID_A`

            UNION

            SELECT
                f.`id` as candidate_filer_pk,
                f.`FILER_ID` as candidate_filer_id,
                committee_filer_id_a.`FILER_ID_B` as committee_filer_id
            FROM calaccess_campaign_browser_filer f
            INNER JOIN (
                SELECT DISTINCT `FILER_ID_A`, `FILER_ID_B`
                FROM FILER_LINKS_CD
                WHERE LINK_TYPE = '12011'
                AND `FILER_ID_B` IS NOT NULL
            ) as committee_filer_id_a
            ON f.`FILER_ID` = committee_filer_id_a.`FILER_ID_A`
            AND f.`FILER_ID` <> committee_filer_id_a.`FILER_ID_B`
        ) as cand2cmte
        INNER JOIN (
            SELECT
             FILERNAME_CD.`FILER_ID` as filer_id,
             REPLACE(TRIM(
                CONCAT(`NAMT`, " ", `NAMF`, " ", `NAML`, " ", `NAMS`)
             ), '  ', ' ') as name
            FROM FILERNAME_CD
            INNER JOIN (
                -- Joining against a subquery that returns the last record
                -- in the source table because there are duplicates and we
                -- do not know of any logical way to better infer the most
                -- recent or complete record.
                SELECT FILER_ID, MAX(`id`) as `id`
                FROM FILERNAME_CD
                GROUP BY 1
            ) as max
            ON FILERNAME_CD.`id` = max.`id`
        ) as distinct_filers
        ON cand2cmte.`committee_filer_id` = distinct_filers.`filer_id`;
        """ % (
            Committee._meta.db_table,
        )
        c.execute(sql)

    def load_pac_filers(self):
        print "- Finding recipient committees not associated with candidates \
and loading into Filer model as PACs"
        c = connection.cursor()
        sql = """
        INSERT INTO %s (
            filer_id,
            status,
            effective_date,
            xref_filer_id,
            filer_type,
            name
        )
        SELECT
         FILERNAME_CD.`FILER_ID` as filer_id,
         FILERNAME_CD.`STATUS` as status,
         FILERNAME_CD.`EFFECT_DT` as effective_date,
         FILERNAME_CD.`XREF_FILER_ID` as xref_filer_id,
        -- Marking these as PAC record in our target data table
         'pac' as filer_type,
        -- Combining and cleaning up the name data from the source
         REPLACE(TRIM(
            CONCAT(`NAMT`, " ", `NAMF`, " ", `NAML`, " ", `NAMS`)
         ), '  ', ' ') as name
        FROM FILERNAME_CD
        INNER JOIN (
            SELECT max_filers.`id`
            FROM (
                -- Query out all the filings with filer IDs that
                --  A) That aren't already in our committee table
                --     as a candidate committee
                --  B) That filed form F460 or F450
                SELECT DISTINCT filings.`FILER_ID`
                FROM FILER_FILINGS_CD filings
                LEFT OUTER JOIN calaccess_campaign_browser_committee committees
                ON filings.`FILER_ID` = committees.`filer_id_raw`
                WHERE `FORM_ID` IN ('F460', 'F450')
                AND committees.id IS NULL
            ) as other_filer_ids
            INNER JOIN (
                -- Link those filing ids with the record that
                -- has the max PK for that ID in the name table
                SELECT `FILER_ID`, MAX(`id`) as `id`
                FROM FILERNAME_CD
                WHERE `FILER_TYPE` = 'RECIPIENT COMMITTEE'
                GROUP BY 1
            ) as max_filers
            ON other_filer_ids.`FILER_ID` = max_filers.`FILER_ID`
        ) as ids
        ON FILERNAME_CD.`id` = ids.`id`;
        """ % (
            Filer._meta.db_table,
        )
        c.execute(sql)

    def load_pac_committees(self):
        """
        Load PAC filers into the committees table.
        """
        print "- Duplicating PAC filers in Committee model"
        c = connection.cursor()
        sql = """
            INSERT INTO %s (
                filer_id,
                filer_id_raw,
                name,
                committee_type
            )
            SELECT
                id,
                filer_id,
                `name`,
                filer_type
            FROM calaccess_campaign_browser_filer
            WHERE filer_type = 'pac'
        """ % (
            Committee._meta.db_table,
        )
        c.execute(sql)
