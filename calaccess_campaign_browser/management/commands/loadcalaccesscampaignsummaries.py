import os
import csv
import MySQLdb
import warnings
from django.db import connection
from calaccess_raw import get_download_directory
from django.utils.datastructures import SortedDict
from calaccess_campaign_browser.models import Summary
from calaccess_campaign_browser.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = "Load refined CAL-ACCESS campaign filing summaries"

    def handle(self, *args, **options):
        self.header("Loading summary totals")
        self.data_dir = get_download_directory()
        self.source_csv = os.path.join(self.data_dir, 'csv', 'smry_cd.csv')
        self.target_csv = os.path.join(
            self.data_dir,
            'csv',
            'smry_cd_transformed.csv'
        )
        self.transform_csv()
        self.load_csv()

    def load_csv(self):
        self.log(" Loading transformed CSV")
        # Ignore MySQL warnings so this can be run with DEBUG=True
        warnings.filterwarnings("ignore", category=MySQLdb.Warning)
        c = connection.cursor()
        sql = """
            LOAD DATA LOCAL INFILE '%s'
            INTO TABLE %s
            FIELDS TERMINATED BY ','
            OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\\r\\n'
            IGNORE 1 LINES (
                filing_id_raw,
                amend_id,
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
        """ % (self.target_csv, Summary._meta.db_table)
        c.execute(sql)

    def transform_csv(self):
        self.log(" Transforming source CSV")
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
        self.log("  Regrouping")
        for r in csv.DictReader(open(self.source_csv, 'rb')):
            uid = "%s-%s" % (r['FILING_ID'], r['AMEND_ID'])
            formkey = "%s-%s" % (r['FORM_TYPE'], r['LINE_ITEM'])
            try:
                field = form2field[formkey]
            except KeyError:
                continue
            try:
                grouped[uid][field] = self.safeamt(r['AMOUNT_A'])
            except KeyError:
                grouped[uid] = SortedDict((
                    ("itemized_monetary_contributions", "\N"),
                    ("unitemized_monetary_contributions", "\N"),
                    ("total_monetary_contributions", "\N"),
                    ("non_monetary_contributions", "\N"),
                    ("total_contributions", "\N"),
                    ("itemized_expenditures", "\N"),
                    ("unitemized_expenditures", "\N"),
                    ("total_expenditures", "\N"),
                    ("ending_cash_balance", "\N"),
                    ("outstanding_debts", "\N")
                ))
                grouped[uid][field] = self.safeamt(r['AMOUNT_A'])
        self.log("  Writing to filesystem")
        out = csv.writer(open(self.target_csv, "wb"))
        outheaders = (
            "filing_id_raw",
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

    def safeamt(self, num):
        if not num:
            return "\N"
        return num
