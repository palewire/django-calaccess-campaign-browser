from django.db import connection
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = "Load refined campaign expenditures from CAL-ACCESS raw data"

    def handle(self, *args, **options):
        self.header("Loading expenditures")
        c = connection.cursor()
        sql = """
        INSERT INTO calaccess_campaign_browser_expenditure (
            cycle_id,
            committee_id,
            filing_id,
            dupe,
            line_item,
            payee_namt,
            payee_namf,
            payee_naml,
            payee_nams,
            expn_dscr,
            payee_zip4,
            g_from_e_f,
            payee_city,
            amount,
            memo_refno,
            expn_code,
            memo_code,
            entity_cd,
            bakref_tid,
            payee_adr1,
            payee_adr2,
            expn_chkno,
            form_type,
            cmte_id,
            xref_schnm,
            xref_match,
            expn_date,
            cum_ytd,
            payee_st,
            tran_id,
            name,
            person_flag,
            raw_org_name
        )
        SELECT
            f.cycle_id as cycle_id,
            f.committee_id as committee_id,
            f.id as filing_id,
            f.is_duplicate,
            e.line_item,
            e.payee_namt,
            e.payee_namf,
            e.payee_naml,
            e.payee_nams,
            e.expn_dscr,
            e.payee_zip4,
            e.g_from_e_f,
            e.payee_city,
            e.amount,
            e.memo_refno,
            e.expn_code,
            e.memo_code,
            e.entity_cd,
            e.bakref_tid,
            e.payee_adr1,
            e.payee_adr2,
            e.expn_chkno,
            e.form_type,
            e.cmte_id,
            e.xref_schnm,
            e.xref_match,
            e.expn_date,
            e.cum_ytd,
            e.payee_st,
            e.tran_id,
            TRIM(
                CASE
                    WHEN e.payee_naml = '' THEN
                        REPLACE(CONCAT(
                            e.bal_name,
                            " ",
                            REPLACE(TRIM(
                                CONCAT(
                                    e.`cand_namt`,
                                    " ",
                                    e.`cand_namf`,
                                    " ",
                                    e.`cand_naml`,
                                    " ",
                                    e.`cand_nams`
                                )
                            ), '  ', ' '),
                            " ",
                            e.juris_dscr,
                            " ",
                            e.offic_dscr
                        ), '  ', ' ')
                    ELSE
                        REPLACE(TRIM(
                            CONCAT(
                                e.`payee_namt`,
                                " ",
                                e.`payee_namf`,
                                " ",
                                e.`payee_naml`,
                                " ",
                                e.`payee_nams`
                            )
                        ), '  ', ' ')
                END
            ) as `name`,
            CASE
                WHEN e.payee_naml = '' THEN
                    false
                WHEN e.payee_naml <> '' AND e.payee_namf = '' THEN
                    false
                ELSE
                    true
            END as `person_flag`,
            CASE
                WHEN e.payee_naml = '' THEN
                    ''
                WHEN e.payee_naml <> '' AND e.payee_namf = '' THEN
                    e.payee_naml
                ELSE
                    ''
            END as `raw_org_name`
        FROM calaccess_campaign_browser_filing as f
        INNER JOIN EXPN_CD as e
        ON f.filing_id_raw = e.filing_id
        AND f.amend_id = e.amend_id
        """
        c.execute(sql)
