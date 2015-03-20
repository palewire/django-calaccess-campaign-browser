import os
import csv
import copy
import MySQLdb
import warnings
import tempfile
from django.db import connection
from calaccess_raw.models import ExpnCd, S496Cd, S498Cd
from calaccess_raw import get_download_directory
from calaccess_campaign_browser.management.commands import CalAccessCommand
from calaccess_campaign_browser.models import Expenditure, Filing, Committee

from ipdb import set_trace as debugger

class Command(CalAccessCommand):
    help = "Load refined campaign expenditures from CAL-ACCESS raw data"

    def set_options(self, *args, **kwargs):
        self.data_dir = os.path.join(get_download_directory(), 'csv')
        self.cursor = connection.cursor()
        # Quarterlies stuff
        self.quarterly_tmp_csv = tempfile.NamedTemporaryFile().name
        self.quarterly_target_csv = os.path.join(
            self.data_dir,
            'expn_cd_transformed.csv'
        )
        # Late filings stuff
        self.late_tmp_csv = tempfile.NamedTemporaryFile().name
        self.late_target_csv = os.path.join(
            self.data_dir,
            's496_cd_transformed.csv'
        )
        self.late_tmp_table = "TMP_%s" % S496Cd._meta.db_table

    def transform_quarterly_expenditures_csv(self):
        self.log("  Marking duplicates")
        self.log("   Dumping CSV sorted by unique identifier")
        sql = """
        SELECT
            `agent_namf`,
            `agent_naml`,
            `agent_nams`,
            `agent_namt`,
            `amend_id`,
            `amount`,
            `bakref_tid`,
            `bal_juris`,
            `bal_name`,
            `bal_num`,
            `cand_namf`,
            `cand_naml`,
            `cand_nams`,
            `cand_namt`,
            `cmte_id`,
            `cum_oth`,
            `cum_ytd`,
            `dist_no`,
            `entity_cd`,
            `expn_chkno`,
            `expn_code`,
            `expn_date`,
            `expn_dscr`,
            `filing_id`,
            `form_type`,
            `g_from_e_f`,
            `juris_cd`,
            `juris_dscr`,
            `line_item`,
            `memo_code`,
            `memo_refno`,
            `off_s_h_cd`,
            `offic_dscr`,
            `office_cd`,
            `payee_adr1`,
            `payee_adr2`,
            `payee_city`,
            `payee_namf`,
            `payee_naml`,
            `payee_nams`,
            `payee_namt`,
            `payee_st`,
            `payee_zip4`,
            `rec_type`,
            `sup_opp_cd`,
            `tran_id`,
            `tres_adr1`,
            `tres_adr2`,
            `tres_city`,
            `tres_namf`,
            `tres_naml`,
            `tres_nams`,
            `tres_namt`,
            `tres_st`,
            `tres_zip4`,
            `xref_match`,
            `xref_schnm`
        FROM %(raw_model)s
        ORDER BY filing_id, tran_id, amend_id DESC
        INTO OUTFILE '%(tmp_csv)s'
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\n'
        """ % dict(
            raw_model=ExpnCd._meta.db_table,
            tmp_csv=self.quarterly_tmp_csv,
        )
        self.cursor.execute(sql)

        INHEADERS = [
            "agent_namf",
            "agent_naml",
            "agent_nams",
            "agent_namt",
            "amend_id",
            "amount",
            "bakref_tid",
            "bal_juris",
            "bal_name",
            "bal_num",
            "cand_namf",
            "cand_naml",
            "cand_nams",
            "cand_namt",
            "cmte_id",
            "cum_oth",
            "cum_ytd",
            "dist_no",
            "entity_cd",
            "expn_chkno",
            "expn_code",
            "expn_date",
            "expn_dscr",
            "filing_id",
            "form_type",
            "g_from_e_f",
            "juris_cd",
            "juris_dscr",
            "line_item",
            "memo_code",
            "memo_refno",
            "off_s_h_cd",
            "offic_dscr",
            "office_cd",
            "payee_adr1",
            "payee_adr2",
            "payee_city",
            "payee_namf",
            "payee_naml",
            "payee_nams",
            "payee_namt",
            "payee_st",
            "payee_zip4",
            "rec_type",
            "sup_opp_cd",
            "tran_id",
            "tres_adr1",
            "tres_adr2",
            "tres_city",
            "tres_namf",
            "tres_naml",
            "tres_nams",
            "tres_namt",
            "tres_st",
            "tres_zip4",
            "xref_match",
            "xref_schnm"
        ]
        OUTHEADERS = copy.copy(INHEADERS)
        OUTHEADERS.append("IS_DUPLICATE")

        self.log("   Marking duplicates in a new CSV")
        # `rU` is read Universal
        # see: https://docs.python.org/2/library/functions.html#open
        with open(self.quarterly_tmp_csv, 'rU') as fin:
            fout = csv.DictWriter(
                open(self.quarterly_target_csv, 'wb'),
                fieldnames=OUTHEADERS
            )
            fout.writeheader()
            last_uid = ''

            reader = csv.DictReader(fin, fieldnames=INHEADERS)

            for row in reader:
                row.pop(None, None)
                uid = '{}-{}'.format(
                    row['filing_id'],
                    row['tran_id']
                )

                if uid != last_uid:
                    row['is_duplicate'] = 0
                    last_uid = uid
                else:
                    row['is_duplicate'] = 1

                try:
                    fout.writerow(row)

                except ValueError, e:
                    continue

    def load_quarterly_expenditures(self):
        pass

    def handle(self, *args, **options):
        self.header("Loading expenditures")
        self.set_options(*args, **options)

        warnings.filterwarnings("ignore", category=MySQLdb.Warning)

        self.log(" Quarterly filings")
        self.transform_quarterly_expenditures_csv()
        self.load_quarterly_expenditures()

        # self.log(" Late filings")
        # self.transform_late_expenditures_csv()
        # self.load_late_expenditures()
