import os
import csv
import copy
import tempfile
import warnings
from optparse import make_option

import MySQLdb

from django.db import connection

from calaccess_raw.models import ExpnCd
from calaccess_raw import get_download_directory
from calaccess_campaign_browser.management.commands import CalAccessCommand
from calaccess_campaign_browser.models import Expenditure, Filing, Committee


custom_options = (
    make_option(
        "--skip-transform-quarterly",
        action="store_false",
        dest="transform_quarterly",
        default=True,
        help="Skip transforming quarterly CSV"
    ),
    make_option(
        "--skip-load-quarterly",
        action="store_false",
        dest="load_quarterly",
        default=True,
        help="Skip loading quarterly CSV to db"
    ),
)


class Command(CalAccessCommand):
    help = "Load refined campaign expenditures from CAL-ACCESS raw data"

    option_list = CalAccessCommand.option_list + custom_options

    def set_options(self, *args, **kwargs):
        self.data_dir = os.path.join(get_download_directory(), 'csv')

        # Make sure directory exists
        os.path.exists(self.data_dir) or os.mkdir(self.data_dir)

        self.cursor = connection.cursor()
        # Quarterlies stuff
        self.quarterly_tmp_csv = tempfile.NamedTemporaryFile().name
        self.quarterly_target_csv = os.path.join(
            self.data_dir,
            'expn_cd_transformed.csv'
        )

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
        OUTHEADERS.append("is_duplicate")

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

                except ValueError:
                    continue

    def load_quarterly_expenditures(self):
        self.log("  Loading CSV")
        self.cursor.execute("DROP TABLE IF EXISTS TMP_EXPN_CD;")
        sql = """
        CREATE TABLE `TMP_EXPN_CD` (
            `AGENT_NAMF` varchar(45),
            `AGENT_NAML` varchar(200),
            `AGENT_NAMS` varchar(10),
            `AGENT_NAMT` varchar(10),
            `AMEND_ID`   int(11),
            `AMOUNT`     decimal(14,2),
            `BAKREF_TID` varchar(20),
            `BAL_JURIS`  varchar(40),
            `BAL_NAME`   varchar(200),
            `BAL_NUM`    varchar(7),
            `CAND_NAMF`  varchar(45),
            `CAND_NAML`  varchar(200),
            `CAND_NAMS`  varchar(10),
            `CAND_NAMT`  varchar(10),
            `CMTE_ID`    varchar(9),
            `CUM_OTH`    decimal(14,2) DEFAULT NULL,
            `CUM_YTD`    decimal(14,2) DEFAULT NULL,
            `DIST_NO`    varchar(3),
            `ENTITY_CD`  varchar(3),
            `EXPN_CHKNO` varchar(20),
            `EXPN_CODE`  varchar(3),
            `EXPN_DATE`  date DEFAULT NULL,
            `EXPN_DSCR`  varchar(400),
            `FILING_ID`  int(11),
            `FORM_TYPE`  varchar(6),
            `G_FROM_E_F` varchar(1),
            `JURIS_CD`   varchar(3),
            `JURIS_DSCR` varchar(40),
            `LINE_ITEM`  int(11),
            `MEMO_CODE`  varchar(1),
            `MEMO_REFNO` varchar(20),
            `OFF_S_H_CD` varchar(1),
            `OFFIC_DSCR` varchar(40),
            `OFFICE_CD`  varchar(3),
            `PAYEE_CITY` varchar(30),
            `PAYEE_NAMF` varchar(45),
            `PAYEE_NAML` varchar(200),
            `PAYEE_NAMS` varchar(10),
            `PAYEE_NAMT` varchar(10),
            `PAYEE_ST`   varchar(2),
            `PAYEE_ZIP4` varchar(10),
            `REC_TYPE`   varchar(4),
            `SUP_OPP_CD` varchar(1),
            `TRAN_ID`    varchar(20),
            `TRES_ADR1`  varchar(55),
            `TRES_ADR2`  varchar(55),
            `TRES_CITY`  varchar(30),
            `TRES_NAMF`  varchar(45),
            `TRES_NAML`  varchar(200),
            `TRES_NAMS`  varchar(10),
            `TRES_NAMT`  varchar(10),
            `TRES_ST`    varchar(2),
            `TRES_ZIP4`  varchar(10),
            `XREF_MATCH` varchar(1),
            `XREF_SCHNM` varchar(2),
            `IS_DUPLICATE` bool
        )
        """

        self.cursor.execute(sql)

        sql = """
            LOAD DATA LOCAL INFILE '%s'
            INTO TABLE TMP_EXPN_CD
            FIELDS TERMINATED BY ','
            OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\\n'
            IGNORE 1 LINES (
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
            `xref_schnm`,
            `is_duplicate`
            )
        """ % (
            self.quarterly_target_csv
        )
        self.cursor.execute(sql)

        self.log("  Merging CSV data with other tables")
        sql = """
            INSERT INTO %(expenditure_model)s (
                cycle_id,
                committee_id,
                filing_id,
                filing_id_raw,
                transaction_id,
                amend_id,
                backreference_transaction_id,
                is_crossreference,
                crossreference_schedule,
                is_duplicate,
                date_received,
                expenditure_description,
                amount,
                candidate_full_name,
                candidate_is_person,
                candidate_committee_id,
                candidate_prefix,
                candidate_first_name,
                candidate_last_name,
                candidate_suffix,
                candidate_entity_type,
                candidate_expense_code,
                payee_prefix,
                payee_first_name,
                payee_last_name,
                payee_suffix,
                payee_address_1,
                payee_address_2,
                payee_city,
                payee_state,
                payee_zipcode
            )
            SELECT
                f.cycle_id as cycle_id,
                f.committee_id as committee_id,
                f.id as filing_id,
                f.filing_id_raw,
                e.tran_id,
                e.amend_id,
                e.bakref_tid,
                e.xref_match,
                e.xref_schnm,
                e.is_duplicate,
                e.expn_date,
                e.expn_dscr,
                e.amount,
                CASE
                    WHEN e.cand_namf <> '' THEN e.cand_naml
                END as candidate_full_name,
                CASE
                    WHEN e.cand_namf <> '' THEN true
                    ELSE false
                END as candidate_is_person,
                c.id,
                COALESCE(e.cand_namt, ''),
                COALESCE(e.cand_namf, ''),
                COALESCE(e.cand_naml, ''),
                COALESCE(e.cand_nams, ''),
                COALESCE(e.entity_cd, ''),
                COALESCE(e.expn_code, ''),
                COALESCE(e.payee_namt, ''),
                COALESCE(e.payee_namf, ''),
                COALESCE(e.payee_naml, ''),
                COALESCE(e.payee_nams, ''),
                COALESCE(e.payee_city, ''),
                COALESCE(e.payee_st, ''),
                COALESCE(e.payee_zip4, '')
            FROM %(filing_model)s as f
            INNER JOIN %(raw_model)s as e
            ON f.filing_id_raw = e.filing_id
            AND f.amend_id = e.amend_id
            LEFT OUTER JOIN %(committee_model)s as c
            ON e.cmte_id = c.xref_filer_id
        """ % dict(
            expenditure_model=Expenditure._meta.db_table,
            filing_model=Filing._meta.db_table,
            raw_model='TMP_EXPN_CD',
            committee_model=Committee._meta.db_table,
        )
        self.cursor.execute(sql)
        self.cursor.execute('DROP TABLE TMP_EXPN_CD;')

    def handle(self, *args, **options):
        self.header("Loading expenditures")
        self.set_options(*args, **options)

        warnings.filterwarnings("ignore", category=MySQLdb.Warning)

        self.log(" Quarterly filings")
        if options['transform_quarterly']:
            self.transform_quarterly_expenditures_csv()

        if options['load_quarterly']:
            self.load_quarterly_expenditures()
