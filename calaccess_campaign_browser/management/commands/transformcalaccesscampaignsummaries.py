import os
import csv
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "- Transform summary totals CSV for loading into database"
        self.csv_path = os.path.join(
            '/home/ben/Code/ccdc/django-calaccess-parser/repo/example',
            'data', 'csv', 'smry_cd.csv'
        )
        grouped = {}
        form2field = {
            # F460
            'A-1': 'itemized_monetary_contributions',
            'A-2': 'unitemized_monetary_contributions',
            'A-3': 'total_monetary_contributions',
            'F460-4': 'non_monetary_contributions',
            'F460-5': 'total_contributions',
            'E-1': 'itemized_expenditures',
            'E-2': 'unitemized_expenditures',
            'E-4': 'total_expenditures',
            'F460-16': 'ending_cash_balance',
            'F460-19': 'outstanding_debts',
            # F450
            'F450-7': 'total_monetary_contributions',
            'F450-8': 'non_monetary_contributions',
            'F450-10': 'total_contributions',
            'F450-1': 'itemized_expenditures',
            'F450-2': 'unitemized_expenditures',
            'E-6': 'total_expenditures',
        }
        print "-- Regrouping source CSV"
        for r in csv.DictReader(open(self.csv_path, 'rb')):
            uid = "%s-%s" % (r['FILING_ID'], r['AMEND_ID'])
            formkey = "%s-%s" % (r['FORM_TYPE'], r['LINE_ITEM'])
            try:
                field = form2field[formkey]
            except KeyError:
                continue
            try:
                grouped[uid][field] = r['AMOUNT_A']
            except KeyError:
                grouped[uid] = SortedDict((
                    ("itemized_monetary_contributions", None),
                    ("unitemized_monetary_contributions", None),
                    ("total_monetary_contributions", None),
                    ("non_monetary_contributions", None),
                    ("total_contributions", None),
                    ("itemized_expenditures", None),
                    ("unitemized_expenditures", None),
                    ("total_expenditures", None),
                    ("ending_cash_balance", None),
                    ("outstanding_debts", None)
                ))
                grouped[uid][field] = r['AMOUNT_A']
        print "-- Writing regrouped data to filesystem"
        out = csv.writer(open("summary_transformed.csv", "wb"))
        outheaders = (
            "filing_id",
            "amend_id",
            "itemized_monetary_contributions",
            "unitemized_monetary_contributions",
            "total_monetary_contributions",
            "non_monetary_contributions",
            "total_contributions",
            "itemized_expenditures",
            "unitemized_expenditures",
            "total_expenditures",
            "ending_cash_balance",
            "outstanding_debts"
        )
        out.writerow(outheaders)
        for uid, data in grouped.items():
            outrow = uid.split("-") + data.values()
            out.writerow(outrow)

    def load_form_F460(self):
        print "-- Form F460"
        c = connection.cursor()
        sql = """
        INSERT INTO calaccess_campaign_browser_summary (
            filing_id,
            committee_id,
            cycle_id,
            form_type,
            dupe,
            itemized_monetary_contributions,
            unitemized_monetary_contributions,
            total_monetary_contributions,
            non_monetary_contributions,
            total_contributions,
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
            COALESCE(
                itemized_monetary_contributions.amount_a,
                0.00
            ) as itemized_monetary_contributions,
            COALESCE(
                unitemized_monetary_contributions.amount_a,
                0.00
            ) as unitemized_monetary_contributions,
            COALESCE(
                total_monetary_contributions.amount_a,
                0.00
            ) as total_monetary_contributions,
            COALESCE(
                non_monetary_contributions.amount_a,
                0.00
            ) as non_monetary_contributions,
            COALESCE(
                total_contributions.amount_a,
                0.00
            ) as total_contributions,
            COALESCE(
                itemized_expenditures.amount_a,
                0.00
            ) as itemized_expenditures,
            COALESCE(
                unitemized_expenditures.amount_a,
                0.00
            ) as unitemized_expenditures,
            COALESCE(total_expenditures.amount_a, 0.00) as total_expenditures,
            COALESCE(
                ending_cash_balance.amount_a,
                0.00
            ) as ending_cash_balance,
            COALESCE(outstanding_debts.amount_a, 0.00) as outstanding_debts
        FROM (
            SELECT
                id,
                committee_id,
                cycle_id,
                form_id,
                dupe,
                filing_id_raw,
                amend_id
            FROM calaccess_campaign_browser_filing
            WHERE form_id = 'F460'
            LIMIT 1000
        ) as f

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'A'
            AND line_item = '1'
        ) as itemized_monetary_contributions
        ON f.filing_id_raw = itemized_monetary_contributions.filing_id
        AND f.amend_id = itemized_monetary_contributions.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'A'
            AND line_item = '2'
        ) as unitemized_monetary_contributions
        ON f.filing_id_raw = unitemized_monetary_contributions.filing_id
        AND f.amend_id = unitemized_monetary_contributions.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'A'
            AND line_item = '3'
        ) as total_monetary_contributions
        ON f.filing_id_raw = total_monetary_contributions.filing_id
        AND f.amend_id = total_monetary_contributions.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F460'
            AND line_item = '4'
        ) as non_monetary_contributions
        ON f.filing_id_raw = non_monetary_contributions.filing_id
        AND f.amend_id = non_monetary_contributions.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F460'
            AND line_item = '5'
        ) as total_contributions
        ON f.filing_id_raw = total_contributions.filing_id
        AND f.amend_id = total_contributions.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'E'
            AND line_item = '1'
        ) as itemized_expenditures
        ON f.filing_id_raw = itemized_expenditures.filing_id
        AND f.amend_id = itemized_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'E'
            AND line_item = '2'
        ) as unitemized_expenditures
        ON f.filing_id_raw = unitemized_expenditures.filing_id
        AND f.amend_id = unitemized_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'E'
            AND line_item = '4'
        ) as total_expenditures
        ON f.filing_id_raw = total_expenditures.filing_id
        AND f.amend_id = total_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F460'
            AND line_item = '16'
        ) as ending_cash_balance
        ON f.filing_id_raw = ending_cash_balance.filing_id
        AND f.amend_id = ending_cash_balance.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F460'
            AND line_item = '19'
        ) as outstanding_debts
        ON f.filing_id_raw = outstanding_debts.filing_id
        AND f.amend_id = outstanding_debts.amend_id
        """
        c.execute(sql)

    def load_form_F450(self):
        print "-- Form F450"
        c = connection.cursor()
        sql = """
        INSERT INTO calaccess_campaign_browser_summary (
            filing_id,
            committee_id,
            cycle_id,
            form_type,
            dupe,
            itemized_monetary_contributions,
            unitemized_monetary_contributions,
            total_monetary_contributions,
            non_monetary_contributions,
            total_contributions,
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
            null as itemized_monetary_contributions,
            null as unitemized_monetary_contributions,
            COALESCE(
                total_monetary_contributions.amount_a,
                0.00
            ) as total_monetary_contributions,
            COALESCE(
                non_monetary_contributions.amount_a,
                0.00
            ) as non_monetary_contributions,
            COALESCE(
                total_contributions.amount_a,
                0.00
            ) as total_contributions,
            COALESCE(
                itemized_expenditures.amount_a,
                0.00
            ) as itemized_expenditures,
            COALESCE(
                unitemized_expenditures.amount_a,
                0.00
            ) as unitemized_expenditures,
            COALESCE(total_expenditures.amount_a, 0.00) as total_expenditures,
            null as ending_cash_balance,
            null as outstanding_debts
        FROM (
            SELECT
                id,
                committee_id,
                cycle_id,
                form_id,
                dupe,
                filing_id_raw,
                amend_id
            FROM calaccess_campaign_browser_filing
            WHERE form_id = 'F450'
        ) as f

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = '7'
        ) as total_monetary_contributions
        ON f.filing_id_raw = total_monetary_contributions.filing_id
        AND f.amend_id = total_monetary_contributions.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = '8'
        ) as non_monetary_contributions
        ON f.filing_id_raw = non_monetary_contributions.filing_id
        AND f.amend_id = non_monetary_contributions.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = '10'
        ) as total_contributions
        ON f.filing_id_raw = total_contributions.filing_id
        AND f.amend_id = total_contributions.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = '1'
        ) as itemized_expenditures
        ON f.filing_id_raw = itemized_expenditures.filing_id
        AND f.amend_id = itemized_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'F450'
            AND line_item = '2'
        ) as unitemized_expenditures
        ON f.filing_id_raw = unitemized_expenditures.filing_id
        AND f.amend_id = unitemized_expenditures.amend_id

        LEFT OUTER JOIN (
            SELECT filing_id, amend_id, amount_a
            FROM SMRY_CD
            WHERE form_type = 'E'
            AND line_item = '6'
        ) as total_expenditures
        ON f.filing_id_raw = total_expenditures.filing_id
        AND f.amend_id = total_expenditures.amend_id
        """
        c.execute(sql)
