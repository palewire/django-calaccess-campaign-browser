import MySQLdb
import warnings
from django.db import connection
from calaccess_campaign_browser import models
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = "Load refined CAL-ACCESS campaign filers and committees"

    def handle(self, *args, **options):
        self.header("Loading filers and committees")

        # Ignore MySQL warnings so this can be run with DEBUG=True
        warnings.filterwarnings("ignore", category=MySQLdb.Warning)

        self.conn = connection.cursor()

        self.drop_temp_tables()
        self.create_temp_tables()
        self.load_cycles()
        self.load_candidate_filers()
        self.create_temp_candidate_committee_tables()
        self.load_candidate_committees()
        self.create_temp_pac_tables()
        self.load_pac_filers()
        self.load_pac_committees()
        self.drop_temp_tables()

    def load_cycles(self):
        self.log(" Loading cycles")
        c = connection.cursor()
        sql = """
            INSERT INTO %(cycle_table)s (`name`)
            SELECT DISTINCT
                CASE
                    WHEN `session_id` %% 2 = 0 THEN `session_id`
                    ELSE `session_id` + 1
                END as cycle
            FROM (
                SELECT `session_id`
                FROM FILER_TO_FILER_TYPE_CD
                GROUP BY 1
                ORDER BY 1 DESC
            ) as sessions;
        """
        sql = sql % dict(cycle_table=models.Cycle._meta.db_table)
        c.execute(sql)

    def create_temp_tables(self):
        """
        Create temporary tables we will use as part of this loader.
        """
        self.log(" Creating temporary tables")

        # Create table with unique filers that eliminates
        # dupes and only keeps the one with the highest incremental ID.
        # We do this because we have not determined any logical way to
        # better infer the most complete record.
        sql = """
        CREATE TEMPORARY TABLE tmp_max_filers (
            INDEX(`filer_id`),
            INDEX(`max_id`)
        ) AS (
            SELECT
                fn.`FILER_ID` as `filer_id`,
                MAX(fn.`id`) as `max_id`
            FROM FILERNAME_CD as fn
            WHERE fn.`FILER_TYPE` = 'CANDIDATE/OFFICEHOLDER'
            OR fn.`FILER_TYPE` = 'RECIPIENT COMMITTEE'
            GROUP BY 1
        );
        """
        self.conn.execute(sql)

        # Create a table with the party affiliation recorded by each filer.
        # This requires brutal removal of duplicates as above.
        sql = """
        CREATE TEMPORARY TABLE tmp_max_filer_metadata (
            INDEX(`filer_id`),
            INDEX(`party`)
        ) AS (
            SELECT
                ft.`FILER_ID` as `filer_id`,
                ft.`PARTY_CD` as `party`,
                ft.`CATEGORY_TYPE` as `level_of_government`,
                ft.`EFFECT_DT` as `effective_date`,
                ft.`ACTIVE` as `status`
            FROM FILER_TO_FILER_TYPE_CD as ft
            INNER JOIN (
                SELECT FILER_ID, MAX(`id`) as `id`
                FROM FILER_TO_FILER_TYPE_CD
                GROUP BY 1
            ) as maxft
            ON ft.`id` = maxft.`id`
        );
        """
        self.conn.execute(sql)

        # Create table that combines the two
        sql = """
        CREATE TEMPORARY TABLE tmp_max_filers_with_metadata (
            INDEX(`filer_id`),
            INDEX(`max_id`)
        ) AS (
            SELECT
                max.`filer_id` as `filer_id`,
                max.`max_id` as `max_id`,
                metadata.party as `party`,
                metadata.level_of_government as `level_of_government`,
                metadata.effective_date as `effective_date`,
                metadata.status as `status`
            FROM tmp_max_filers as max
            INNER JOIN tmp_max_filer_metadata as metadata
            ON max.`filer_id` = metadata.`filer_id`
        );
        """
        self.conn.execute(sql)

    def drop_temp_tables(self):
        """
        Drop the temporary tables we created as part of this loader.
        """
        self.log(" Dropping temporary tables")
        table_list = [
            "tmp_max_filers",
            "tmp_max_filer_metadata",
            "tmp_max_filers_with_metadata",
            "tmp_cand2cmte",
            "tmp_other_filers",
            "tmp_max_other_filers",
        ]
        sql = """DROP TABLE IF EXISTS %s;"""
        for t in table_list:
            self.conn.execute(sql % t)

    def load_candidate_filers(self):
        """
        Load all of the distinct candidate filers into the Filer model.
        """
        self.log(" Loading candidate filers")

        sql = """
        INSERT INTO %s (
            filer_id_raw,
            status,
            effective_date,
            xref_filer_id,
            filer_type,
            name,
            party
        )
        SELECT
            fn.`FILER_ID` as filer_id,
            fn.`STATUS` as status,
            fn.`EFFECT_DT` as effective_date,
            fn.`XREF_FILER_ID` as xref_filer_id,
            'cand' as filer_type,
            REPLACE(
                TRIM(
                    CONCAT(`NAMT`, " ", `NAMF`, " ", `NAML`, " ", `NAMS`)
                ),
                '  ',
                ' '
            ) as name,
            max.`party`
        FROM FILERNAME_CD as fn
        INNER JOIN tmp_max_filers_with_metadata as max
        ON fn.`id` = max.`max_id`
        WHERE fn.`FILER_TYPE` = 'CANDIDATE/OFFICEHOLDER';
        """ % (
            models.Filer._meta.db_table,
        )

        self.conn.execute(sql)

    def create_temp_candidate_committee_tables(self):
        self.log(" Creating more temporary tables")
        # Join together via a UNION to return the committee filer ids linked
        # to candidate filer records from either direction (i.e. A or B)
        sql = """
            CREATE TEMPORARY TABLE tmp_cand2cmte (
                INDEX(`candidate_filer_pk`),
                INDEX(`candidate_filer_id`),
                INDEX(`committee_filer_id`)
            )
            SELECT
                f.`id` as candidate_filer_pk,
                f.`filer_id_raw` as candidate_filer_id,
                committee_filer_id_a.`FILER_ID_A` as committee_filer_id
            FROM %(filer_model)s f
            INNER JOIN (
                SELECT DISTINCT `FILER_ID_A`, `FILER_ID_B`
                FROM FILER_LINKS_CD
                WHERE LINK_TYPE = '12011'
                AND `FILER_ID_A` IS NOT NULL
            ) as committee_filer_id_a
            ON f.`filer_id_raw` = committee_filer_id_a.`FILER_ID_B`
            AND f.`filer_id_raw` <> committee_filer_id_a.`FILER_ID_A`

            UNION

            SELECT
                f.`id` as candidate_filer_pk,
                f.`filer_id_raw` as candidate_filer_id,
                committee_filer_id_a.`FILER_ID_B` as committee_filer_id
            FROM %(filer_model)s f
            INNER JOIN (
                SELECT DISTINCT `FILER_ID_A`, `FILER_ID_B`
                FROM FILER_LINKS_CD
                WHERE LINK_TYPE = '12011'
                AND `FILER_ID_B` IS NOT NULL
            ) as committee_filer_id_a
            ON f.`filer_id_raw` = committee_filer_id_a.`FILER_ID_A`
            AND f.`filer_id_raw` <> committee_filer_id_a.`FILER_ID_B`;
        """ % dict(filer_model=models.Filer._meta.db_table,)

        self.conn.execute(sql)

    def load_candidate_committees(self):
        """
        Loads the committees associated with candidates into the Committee
        model.
        """
        self.log(" Loading candidate committees")

        sql = """
        INSERT INTO %s (
            filer_id,
            filer_id_raw,
            xref_filer_id,
            name,
            committee_type,
            party,
            level_of_government,
            effective_date,
            status
        )
        SELECT
            tmp_cand2cmte.`candidate_filer_pk` as filer_id,
            distinct_filers.`filer_id` as filer_id_raw,
            distinct_filers.`xref_filer_id` as xref_filer_id,
            distinct_filers.`name` as name,
            'cand' as committee_type,
            distinct_filers.`party` as party,
            distinct_filers.`level_of_government` as level_of_government,
            distinct_filers.`effective_date` as effective_date,
            distinct_filers.`status` as status
        FROM tmp_cand2cmte
        INNER JOIN (
            SELECT
                fn.`FILER_ID` as filer_id,
                fn.`XREF_FILER_ID` as xref_filer_id,
                REPLACE(
                    TRIM(
                        CONCAT(`NAMT`, " ", `NAMF`, " ", `NAML`, " ", `NAMS`)
                    ),
                    '  ',
                    ' '
                ) as name,
                max.`party`,
                max.`level_of_government`,
                max.`effective_date`,
                max.`status`
            FROM FILERNAME_CD as fn
            INNER JOIN tmp_max_filers_with_metadata as max
            ON fn.`id` = max.`max_id`
        ) as distinct_filers
        ON tmp_cand2cmte.`committee_filer_id` = distinct_filers.`filer_id`;
        """ % (models.Committee._meta.db_table,)

        self.conn.execute(sql)

    def create_temp_pac_tables(self):
        """
        Another set of temporary tables that can't be created until the
        candidates are loaded into our clean models.
        """
        self.log(" Creating yet more temporary tables")

        # Create a table of all committee filer ids that are not
        # linked to candidates.
        #
        # That means committees that:
        #
        #   A) Aren't already in our committee table
        #      as a candidate committee
        #
        #   B) Filed form F460 or F450
        #
        sql = """
            CREATE TEMPORARY TABLE tmp_other_filers (
                index(`filer_id`)
            ) AS (
                SELECT
                    DISTINCT f.`FILER_ID`
                FROM FILER_FILINGS_CD as f
                LEFT OUTER JOIN %(committee_model)s as c
                ON f.`FILER_ID` = c.`filer_id_raw`
                WHERE `FORM_ID` IN ('F460', 'F450')
                AND c.id IS NULL
            );
        """ % dict(committee_model=models.Committee._meta.db_table,)
        self.conn.execute(sql)

        # Now connect those with the FILERNAME_CD table and get
        # the maximum PK there to kill the duplicates
        sql = """
        CREATE TEMPORARY TABLE tmp_max_other_filers (
            index(`filer_id`),
            index(`max_id`)
        ) AS (
            SELECT
                f.`FILER_ID`,
                MAX(`id`) as `max_id`
            FROM FILERNAME_CD as f
            INNER JOIN tmp_other_filers as t
            ON f.`FILER_ID` = t.`filer_id`
            WHERE f.`FILER_TYPE` = 'RECIPIENT COMMITTEE'
            GROUP BY 1
        );
        """
        self.conn.execute(sql)

    def load_pac_filers(self):
        self.log(" Loading PAC filers")
        sql = """
        INSERT INTO %s (
            filer_id_raw,
            status,
            effective_date,
            xref_filer_id,
            filer_type,
            name,
            party
        )
        SELECT
            fn.`FILER_ID` as filer_id,
            fn.`STATUS` as status,
            fn.`EFFECT_DT` as effective_date,
            fn.`XREF_FILER_ID` as xref_filer_id,
            'pac' as filer_type,
            REPLACE(
                TRIM(
                    CONCAT(`NAMT`, " ", `NAMF`, " ", `NAML`, " ", `NAMS`)
                ),
                '  ',
                ' '
            ) as name,
            tmp_max_filer_metadata.`party`
        FROM FILERNAME_CD as fn
        INNER JOIN tmp_max_other_filers as max
        ON fn.`id` = max.`max_id`
        LEFT OUTER JOIN tmp_max_filer_metadata
        ON fn.`FILER_ID` = tmp_max_filer_metadata.`filer_id`
        WHERE fn.`FILER_TYPE` = 'RECIPIENT COMMITTEE';
        """ % (models.Filer._meta.db_table,)

        self.conn.execute(sql)

    def load_pac_committees(self):
        """
        Load PAC filers into the Committee model.
        """
        self.log(" Loading PAC committees")

        sql = """
            INSERT INTO %(committee_model)s (
                filer_id,
                filer_id_raw,
                xref_filer_id,
                name,
                committee_type,
                party,
                level_of_government,
                effective_date,
                status
            )
            SELECT
                %(filer_model)s.`id`,
                %(filer_model)s.`filer_id_raw`,
                %(filer_model)s.`xref_filer_id`,
                %(filer_model)s.`name`,
                %(filer_model)s.`filer_type`,
                %(filer_model)s.`party`,
                metadata.`level_of_government`,
                metadata.`effective_date`,
                metadata.`status`
            FROM %(filer_model)s
            LEFT OUTER JOIN tmp_max_filer_metadata as metadata
            ON %(filer_model)s.`filer_id_raw` = metadata.`filer_id`
            WHERE filer_type = 'pac';
        """ % dict(
            committee_model=models.Committee._meta.db_table,
            filer_model=models.Filer._meta.db_table,
        )

        self.conn.execute(sql)
