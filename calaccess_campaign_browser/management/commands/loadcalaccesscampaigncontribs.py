from django.db import connection
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.models import Contribution


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "- Loading contributions"
        c = connection.cursor()
        c.execute('DELETE FROM %s' % Contribution._meta.db_table)
        sql = """
            INSERT INTO calaccess_campaign_browser_contribution (
                cycle_id,
                committee_id,
                filing_id,
                dupe,
                ctrib_namt,
                ctrib_occ,
                ctrib_nams,
                line_item,
                rec_type,
                ctrib_namf,
                date_thru,
                ctrib_naml,
                ctrib_self,
                rcpt_date,
                ctrib_zip4,
                ctrib_st,
                ctrib_adr1,
                ctrib_adr2,
                memo_refno,
                intr_st,
                memo_code,
                intr_self,
                intr_occ,
                intr_emp,
                entity_cd,
                intr_cmteid,
                ctrib_city,
                bakref_tid,
                tran_type,
                intr_adr2,
                cum_ytd,
                intr_adr1,
                form_type,
                intr_city,
                cmte_id,
                xref_schnm,
                ctrib_emp,
                xref_match,
                cum_oth,
                ctrib_dscr,
                intr_namt,
                intr_nams,
                amount,
                intr_naml,
                intr_zip4,
                intr_namf,
                tran_id,
                raw_org_name,
                person_flag
            )
            SELECT
                f.cycle_id as cycle_id,
                f.committee_id as committee_id,
                f.id as filing_id,
                f.dupe,
                r.ctrib_namt,
                r.ctrib_occ,
                r.ctrib_nams,
                r.line_item,
                r.rec_type,
                r.ctrib_namf,
                r.date_thru,
                r.ctrib_naml,
                r.ctrib_self,
                r.rcpt_date,
                r.ctrib_zip4,
                r.ctrib_st,
                r.ctrib_adr1,
                r.ctrib_adr2,
                r.memo_refno,
                r.intr_st,
                r.memo_code,
                r.intr_self,
                r.intr_occ,
                r.intr_emp,
                r.entity_cd,
                r.intr_cmteid,
                r.ctrib_city,
                r.bakref_tid,
                r.tran_type,
                r.intr_adr2,
                r.cum_ytd,
                r.intr_adr1,
                r.form_type,
                r.intr_city,
                r.cmte_id,
                r.xref_schnm,
                r.ctrib_emp,
                r.xref_match,
                r.cum_oth,
                r.ctrib_dscr,
                r.intr_namt,
                r.intr_nams,
                r.amount,
                r.intr_naml,
                r.intr_zip4,
                r.intr_namf,
                r.tran_id,
                CASE
                    WHEN r.ctrib_namf <> '' THEN r.ctrib_emp
                    ELSE r.ctrib_naml
                END as raw_org_nam,
                CASE
                    WHEN r.ctrib_namf <> '' THEN true
                    ELSE false
                END as person_flag
            FROM calaccess_campaign_browser_filing as f
            INNER JOIN RCPT_CD as r
            ON f.filing_id_raw = r.filing_id
            AND f.amend_id = r.amend_id
        """
        c.execute(sql)
