import os
import csv
import tempfile
from django.db import connection
from calaccess_raw import get_download_directory
from django.utils.datastructures import SortedDict
from calaccess_campaign_browser.management.commands import CalAccessCommand
from calaccess_campaign_browser.models import Summary, Filing, Committee


class Command(CalAccessCommand):

    def handle(self, *args, **options):
        self.header("Loading summary totals")
        self.set_options(*args, **options)
        # Ignore MySQL "note" warnings so this can be run with DEBUG=True
        self.cursor.execute("""SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0;""")
        self.transform_csv()
        self.load_csv()
        # Revert database to default "note" warning behavior
        self.cursor.execute("""SET SQL_NOTES=@OLD_SQL_NOTES;""")

    def set_options(self, *args, **kwargs):
        self.data_dir = get_download_directory()
        self.cursor = connection.cursor()
        self.source_csv = os.path.join(self.data_dir, 'csv', 'smry_cd.csv')
        self.target_csv = os.path.join(
            self.data_dir,
            'csv',
            'smry_cd_transformed.csv'
        )
        #self.sum_tmp_csv = tempfile.NamedTemporaryFile().name
        self.sum_tmp_table = "TMP_%s" % Summary._meta.db_table

    def load_csv(self):
        self.log(" Loading transformed CSV")

        self.cursor.execute("DROP TABLE IF EXISTS %s" % self.sum_tmp_table)

        sql = """
            CREATE TABLE `%(tmp_table)s` (
                `FILING_ID` int(11) NOT NULL,
                `FILING_ID_RAW` int(11) NOT NULL,
                `AMEND_ID` int(11) NOT NULL,
                `ITEMIZED_MONETARY_CONTRIBUTIONS` decimal(16, 2),
                `UNITEMIZED_MONETARY_CONTRIBUTIONS` decimal(16, 2),
                `TOTAL_MONETARY_CONTRIBUTIONS` decimal(16, 2),
                `NON_MONETARY_CONTRIBUTIONS` decimal(16, 2),
                `TOTAL_CONTRIBUTIONS` decimal(16, 2),
                `ITEMIZED_EXPENDITURES` decimal(16, 2),
                `UNITEMIZED_EXPENDITURES` decimal(16, 2),
                `TOTAL_EXPENDITURES` decimal(16, 2),
                `ENDING_CASH_BALANCE` decimal(16, 2),
                `OUTSTANDING_DEBTS` decimal(16, 2)
            )
        """ % dict(
            tmp_table=self.sum_tmp_table,
        )
        self.cursor.execute(sql)

        sql = """
            LOAD DATA LOCAL INFILE '%(target_csv)s'
            INTO TABLE %(tmp_table)s
            FIELDS TERMINATED BY ','
            OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\\n'
            IGNORE 1 LINES (
                `FILING_ID`,
                `FILING_ID_RAW`,
                `AMEND_ID`,
                `ITEMIZED_MONETARY_CONTRIBUTIONS`,
                `UNITEMIZED_MONETARY_CONTRIBUTIONS`,
                `TOTAL_MONETARY_CONTRIBUTIONS`,
                `NON_MONETARY_CONTRIBUTIONS`,
                `TOTAL_CONTRIBUTIONS`,
                `ITEMIZED_EXPENDITURES`,
                `UNITEMIZED_EXPENDITURES`,
                `TOTAL_EXPENDITURES`,
                `ENDING_CASH_BALANCE`,
                `OUTSTANDING_DEBTS`
            )
        """ % dict(
            target_csv=self.target_csv,
            tmp_table=self.sum_tmp_table,
        )
        self.cursor.execute(sql)

        self.log("  Merging CSV data with other tables")
        sql = """
            INSERT INTO %(sum_model)s (
                filing_id,
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
        """ % dict (
            sum_model=Summary._meta.db_table,
            filing_model=Filing._meta.db_table,
            raw_model=self.sum_tmp_table,
            # committee_model=Committee._meta.db_table,
        )
        self.cursor.execute(sql)
        self.cursor.execute("DROP TABLE %s" % self.sum_tmp_table)

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
            "filing_id",
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
