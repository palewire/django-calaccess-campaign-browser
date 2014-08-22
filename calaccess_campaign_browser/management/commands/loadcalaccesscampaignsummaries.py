from django.db import connection
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.models import Summary


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "- Loading summary totals for filings"
        c = connection.cursor()
        c.execute('DELETE FROM %s' % Summary._meta.db_table)
        self.load_form_F460()
        self.load_form_F450()

    def load_form_F460(self):
        print "-- Loading summary totals for Form F460"
        c = connection.cursor()
        sql = """
        INSERT INTO calaccess_campaign_browser_summary (
            filing_id,
            committee_id,
            cycle_id,
            form_type,
            dupe,
            itemized_monetary_contribs,
            unitemized_monetary_contribs,
            total_monetary_contribs,
            non_monetary_contribs,
            total_contribs,
            itemized_expenditures,
            unitemized_expenditures,
            total_expenditures,
            ending_cash_balance,
            outstanding_debts
        )
        SELECT
            f.id as filing_id,
            f.committee_id,
            f.cycle_id,
            f.form_id as form_type,
            f.dupe,
            COALESCE(itemized_monetary_contribs.amount_a, 0) as itemized_monetary_contribs,
            COALESCE(unitemized_monetary_contribs.amount_a, 0) as unitemized_monetary_contribs,
            COALESCE(total_monetary_contribs.amount_a, 0) as total_monetary_contribs,
            COALESCE(non_monetary_contribs.amount_a, 0) as non_monetary_contribs,
            COALESCE(total_contribs.amount_a, 0) as total_contribs,
            COALESCE(itemized_expenditures.amount_a, 0) as itemized_expenditure,
            COALESCE(unitemized_expenditures.amount_a, 0) as unitemized_expenditure,
            COALESCE(total_expenditures.amount_a, 0) as total_expenditures,
            COALESCE(ending_cash_balance.amount_a, 0) as ending_cash_balance,
            COALESCE(outstanding_debts.amount_a, 0) as outstanding_debts

        FROM calaccess_campaign_browser_filing as f

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'A'
            AND line_item = 1
        ) as itemized_monetary_contribs
        ON f.filing_id_raw = itemized_monetary_contribs.filing_id
        AND f.amend_id = itemized_monetary_contribs.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'A'
            AND line_item = 2
        ) as unitemized_monetary_contribs
        ON f.filing_id_raw = unitemized_monetary_contribs.filing_id
        AND f.amend_id = unitemized_monetary_contribs.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'A'
            AND line_item = 3
        ) as total_monetary_contribs
        ON f.filing_id_raw = total_monetary_contribs.filing_id
        AND f.amend_id = total_monetary_contribs.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F460'
            AND line_item = 4
        ) as non_monetary_contribs
        ON f.filing_id_raw = non_monetary_contribs.filing_id
        AND f.amend_id = non_monetary_contribs.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F460'
            AND line_item = 5
        ) as total_contribs
        ON f.filing_id_raw = total_contribs.filing_id
        AND f.amend_id = total_contribs.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'E'
            AND line_item = 1
        ) as itemized_expenditures
        ON f.filing_id_raw = itemized_expenditures.filing_id
        AND f.amend_id = itemized_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'E'
            AND line_item = 2
        ) as unitemized_expenditures
        ON f.filing_id_raw = unitemized_expenditures.filing_id
        AND f.amend_id = unitemized_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'E'
            AND line_item = 4
        ) as total_expenditures
        ON f.filing_id_raw = total_expenditures.filing_id
        AND f.amend_id = total_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F460'
            AND line_item = 16
        ) as ending_cash_balance
        ON f.filing_id_raw = ending_cash_balance.filing_id
        AND f.amend_id = ending_cash_balance.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F460'
            AND line_item = 19
        ) as outstanding_debts
        ON f.filing_id_raw = outstanding_debts.filing_id
        AND f.amend_id = outstanding_debts.amend_id

        WHERE f.form_id = 'F460'
        """
        c.execute(sql)

    def load_form_f450(self):
        print "-- Loading summary totals for Form F450"
        c = connection.cursor()
        sql = """
        INSERT INTO calaccess_campaign_browser_summary (
            filing_id,
            committee_id,
            cycle_id,
            form_type,
            dupe,
            itemized_monetary_contribs,
            unitemized_monetary_contribs,
            total_monetary_contribs,
            non_monetary_contribs,
            total_contribs,
            itemized_expenditures,
            unitemized_expenditures,
            total_expenditures,
            ending_cash_balance,
            outstanding_debts
        )
        SELECT
            f.id as filing_id,
            f.committee_id,
            f.cycle_id,
            f.form_id as form_type,
            f.dupe,
            null as itemized_monetary_contribs,
            null as unitemized_monetary_contribs,
            COALESCE(total_monetary_contribs.amount_a, 0) as total_monetary_contribs,
            COALESCE(non_monetary_contribs.amount_a, 0) as non_monetary_contribs,
            COALESCE(total_contribs.amount_a, 0) as total_contribs,
            COALESCE(itemized_expenditures.amount_a, 0) as itemized_expenditure,
            COALESCE(unitemized_expenditures.amount_a, 0) as unitemized_expenditure,
            COALESCE(total_expenditures.amount_a, 0) as total_expenditures,
            null as ending_cash_balance,
            null as outstanding_debts

        FROM calaccess_campaign_browser_filing as f

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = 7
        ) as total_monetary_contribs
        ON f.filing_id_raw = total_monetary_contribs.filing_id
        AND f.amend_id = total_monetary_contribs.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = 8
        ) as non_monetary_contribs
        ON f.filing_id_raw = non_monetary_contribs.filing_id
        AND f.amend_id = non_monetary_contribs.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = 10
        ) as total_contribs
        ON f.filing_id_raw = total_contribs.filing_id
        AND f.amend_id = total_contribs.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = 1
        ) as itemized_expenditures
        ON f.filing_id_raw = itemized_expenditures.filing_id
        AND f.amend_id = itemized_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = 2
        ) as unitemized_expenditures
        ON f.filing_id_raw = unitemized_expenditures.filing_id
        AND f.amend_id = unitemized_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'E'
            AND line_item = 6
        ) as total_expenditures
        ON f.filing_id_raw = total_expenditures.filing_id
        AND f.amend_id = total_expenditures.amend_id

        WHERE f.form_id = 'F450'
        """
        c.execute(sql)
