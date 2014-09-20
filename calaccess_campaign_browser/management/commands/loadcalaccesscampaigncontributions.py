from django.db import connection
from calaccess_raw.models import RcptCd
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.models import Contribution, Filing


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "- Loading contributions"
        c = connection.cursor()
        sql = """
            INSERT INTO %(contribs_model)s (
                cycle_id,
                committee_id,
                filing_id,
                transaction_id,
                amend_id,
                backreference_transaction_id,
                is_crossreference,
                crossreference_schedule,
                is_duplicate,
                transaction_type,
                date_received,
                contribution_description,
                amount,
                contributor_full_name,
                contributor_is_person,
                contributor_prefix,
                contributor_first_name,
                contributor_last_name,
                contributor_suffix,
                contributor_address_1,
                contributor_address_2,
                contributor_city,
                contributor_state,
                contributor_zipcode,
                contributor_occupation,
                contributor_employer,
                contributor_selfemployed,
                intermediary_prefix,
                intermediary_first_name,
                intermediary_last_name,
                intermediary_suffix,
                intermediary_address_1,
                intermediary_address_2,
                intermediary_city,
                intermediary_state,
                intermediary_zipcode,
                intermediary_occupation,
                intermediary_employer,
                intermediary_selfemployed,
                intermediary_committee_id
            )
            SELECT
                f.cycle_id as cycle_id,
                f.committee_id as committee_id,
                f.id as filing_id,
                r.tran_id,
                r.amend_id,
                r.bakref_tid,
                r.xref_match,
                r.xref_schnm,
                false,
                r.tran_type,
                r.rcpt_date,
                r.ctrib_dscr,
                r.amount,
                CASE
                    WHEN r.ctrib_namf <> '' THEN r.ctrib_emp
                    ELSE r.ctrib_naml
                END as contributor_full_name,
                CASE
                    WHEN r.ctrib_namf <> '' THEN true
                    ELSE false
                END as contributor_is_person,
                r.ctrib_namt,
                r.ctrib_namf,
                r.ctrib_naml,
                r.ctrib_nams,
                r.ctrib_adr1,
                r.ctrib_adr2,
                r.ctrib_city,
                r.ctrib_st,
                r.ctrib_zip4,
                r.ctrib_occ,
                r.ctrib_emp,
                r.ctrib_self,
                r.intr_namt,
                r.intr_namf,
                r.intr_naml,
                r.intr_nams,
                r.intr_adr1,
                r.intr_adr2,
                r.intr_city,
                r.intr_st,
                r.intr_zip4,
                r.intr_occ,
                r.intr_emp,
                r.intr_self,
                r.intr_cmteid
            FROM %(filing_model)s as f
            INNER JOIN %(raw_model)s as r
            ON f.filing_id_raw = r.filing_id
            AND f.amend_id = r.amend_id
        """ % dict(
            contribs_model=Contribution._meta.db_table,
            filing_model=Filing._meta.db_table,
            raw_model=RcptCd._meta.db_table,
        )
        c.execute(sql)
