import os
import csv
import copy
import MySQLdb
import warnings
import tempfile
from django.db import connection
from calaccess_raw.models import RcptCd, S497Cd
from calaccess_raw import get_download_directory
from calaccess_campaign_browser.management.commands import CalAccessCommand
from calaccess_campaign_browser.models import Contribution, Filing, Committee


class Command(CalAccessCommand):
    help = "Load refined campaign contributions from CAL-ACCESS raw data"

    def handle(self, *args, **options):
        self.header("Loading contributions")
        self.set_options(*args, **options)

        # Ignore MySQL warnings so this can be run with DEBUG=True
        warnings.filterwarnings("ignore", category=MySQLdb.Warning)

        self.log(" Quarterly filings")
        self.transform_quarterly_contributions_csv()
        self.load_quarterly_contributions()
        self.log(" Late filings")
        self.transform_late_contributions_csv()
        self.load_late_contributions()

    def set_options(self, *args, **kwargs):
        self.data_dir = os.path.join(get_download_directory(), 'csv')
        self.cursor = connection.cursor()
        # Quarterlies stuff
        self.quarterly_tmp_csv = tempfile.NamedTemporaryFile().name
        self.quarterly_target_csv = os.path.join(
            self.data_dir,
            'rcpt_cd_transformed.csv'
        )
        # Late filings stuff
        self.late_tmp_csv = tempfile.NamedTemporaryFile().name
        self.late_target_csv = os.path.join(
            self.data_dir,
            's497_cd_transformed.csv'
        )
        self.late_tmp_table = "TMP_%s" % S497Cd._meta.db_table

    def transform_late_contributions_csv(self):
        self.log("  Marking duplicates")
        self.log("   Dumping CSV sorted by unique identifier")
        sql = """
        SELECT
            `S497_CD`.`FILING_ID`,
            `S497_CD`.`AMEND_ID`,
            `S497_CD`.`LINE_ITEM`,
            `S497_CD`.`REC_TYPE`,
            `S497_CD`.`FORM_TYPE`,
            `S497_CD`.`TRAN_ID`,
            `S497_CD`.`ENTITY_CD`,
            `S497_CD`.`ENTY_NAML`,
            `S497_CD`.`ENTY_NAMF`,
            `S497_CD`.`ENTY_NAMT`,
            `S497_CD`.`ENTY_NAMS`,
            `S497_CD`.`ENTY_CITY`,
            `S497_CD`.`ENTY_ST`,
            `S497_CD`.`ENTY_ZIP4`,
            `S497_CD`.`CTRIB_EMP`,
            `S497_CD`.`CTRIB_OCC`,
            `S497_CD`.`CTRIB_SELF`,
            `S497_CD`.`ELEC_DATE`,
            `S497_CD`.`CTRIB_DATE`,
            `S497_CD`.`DATE_THRU`,
            `S497_CD`.`AMOUNT`,
            `S497_CD`.`CMTE_ID`,
            `S497_CD`.`CAND_NAML`,
            `S497_CD`.`CAND_NAMF`,
            `S497_CD`.`CAND_NAMT`,
            `S497_CD`.`CAND_NAMS`,
            `S497_CD`.`OFFICE_CD`,
            `S497_CD`.`OFFIC_DSCR`,
            `S497_CD`.`JURIS_CD`,
            `S497_CD`.`JURIS_DSCR`,
            `S497_CD`.`DIST_NO`,
            `S497_CD`.`OFF_S_H_CD`,
            `S497_CD`.`BAL_NAME`,
            `S497_CD`.`BAL_NUM`,
            `S497_CD`.`BAL_JURIS`,
            `S497_CD`.`MEMO_CODE`,
            `S497_CD`.`MEMO_REFNO`,
            `S497_CD`.`BAL_ID`,
            `S497_CD`.`CAND_ID`,
            `S497_CD`.`SUP_OFF_CD`,
            `S497_CD`.`SUP_OPP_CD`
        FROM %(raw_model)s
        ORDER BY FILING_ID, TRAN_ID, AMEND_ID DESC
        INTO OUTFILE '%(tmp_csv)s'
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\n'
        """ % dict(
            raw_model=S497Cd._meta.db_table,
            tmp_csv=self.late_tmp_csv,
        )
        self.cursor.execute(sql)

        INHEADERS = [
            "FILING_ID",
            "AMEND_ID",
            "LINE_ITEM",
            "REC_TYPE",
            "FORM_TYPE",
            "TRAN_ID",
            "ENTITY_CD",
            "ENTY_NAML",
            "ENTY_NAMF",
            "ENTY_NAMT",
            "ENTY_NAMS",
            "ENTY_CITY",
            "ENTY_ST",
            "ENTY_ZIP4",
            "CTRIB_EMP",
            "CTRIB_OCC",
            "CTRIB_SELF",
            "ELEC_DATE",
            "CTRIB_DATE",
            "DATE_THRU",
            "AMOUNT",
            "CMTE_ID",
            "CAND_NAML",
            "CAND_NAMF",
            "CAND_NAMT",
            "CAND_NAMS",
            "OFFICE_CD",
            "OFFIC_DSCR",
            "JURIS_CD",
            "JURIS_DSCR",
            "DIST_NO",
            "OFF_S_H_CD",
            "BAL_NAME",
            "BAL_NUM",
            "BAL_JURIS",
            "MEMO_CODE",
            "MEMO_REFNO",
            "BAL_ID",
            "CAND_ID",
            "SUP_OFF_CD",
            "SUP_OPP_CD"
        ]
        OUTHEADERS = copy.copy(INHEADERS)
        OUTHEADERS.append("IS_DUPLICATE")

        self.log("   Marking duplicates in a new CSV")
        with open(self.late_tmp_csv, 'r') as fin:
            fout = csv.DictWriter(
                open(self.late_target_csv, 'wb'),
                fieldnames=OUTHEADERS
            )
            fout.writeheader()
            last_uid = ''
            for r in csv.DictReader(fin, fieldnames=INHEADERS):
                r.pop(None, None)
                uid = '%s-%s' % (r['FILING_ID'], r['TRAN_ID'])
                if uid != last_uid:
                    r['IS_DUPLICATE'] = 0
                    last_uid = uid
                else:
                    r['IS_DUPLICATE'] = 1
                try:
                    fout.writerow(r)
                except ValueError:
                    continue

    def load_late_contributions(self):
        self.log("  Loading CSV")

        self.cursor.execute("DROP TABLE IF EXISTS %s" % self.late_tmp_table)

        sql = """
        CREATE TABLE `%(tmp_table)s` (
          `FILING_ID` int(11) NOT NULL,
          `AMEND_ID` int(11) NOT NULL,
          `LINE_ITEM` int(11) NOT NULL,
          `REC_TYPE` varchar(4) NOT NULL,
          `FORM_TYPE` varchar(6) NOT NULL,
          `TRAN_ID` varchar(20) NOT NULL,
          `ENTITY_CD` varchar(3) NOT NULL,
          `ENTY_NAML` varchar(200) NOT NULL,
          `ENTY_NAMF` varchar(45) NOT NULL,
          `ENTY_NAMT` varchar(10) NOT NULL,
          `ENTY_NAMS` varchar(10) NOT NULL,
          `ENTY_CITY` varchar(30) NOT NULL,
          `ENTY_ST` varchar(2) NOT NULL,
          `ENTY_ZIP4` varchar(10) NOT NULL,
          `CTRIB_EMP` varchar(200) NOT NULL,
          `CTRIB_OCC` varchar(60) NOT NULL,
          `CTRIB_SELF` varchar(1) NOT NULL,
          `ELEC_DATE` date NOT NULL,
          `CTRIB_DATE` date NOT NULL,
          `DATE_THRU` date NOT NULL,
          `AMOUNT` decimal(16,2) NOT NULL,
          `CMTE_ID` varchar(9) NOT NULL,
          `CAND_NAML` varchar(200) NOT NULL,
          `CAND_NAMF` varchar(45) NOT NULL,
          `CAND_NAMT` varchar(10) NOT NULL,
          `CAND_NAMS` varchar(10) NOT NULL,
          `OFFICE_CD` varchar(3) NOT NULL,
          `OFFIC_DSCR` varchar(40) NOT NULL,
          `JURIS_CD` varchar(3) NOT NULL,
          `JURIS_DSCR` varchar(40) NOT NULL,
          `DIST_NO` varchar(3) NOT NULL,
          `OFF_S_H_CD` varchar(1) NOT NULL,
          `BAL_NAME` varchar(200) NOT NULL,
          `BAL_NUM` varchar(7) NOT NULL,
          `BAL_JURIS` varchar(40) NOT NULL,
          `MEMO_CODE` varchar(1) NOT NULL,
          `MEMO_REFNO` varchar(20) NOT NULL,
          `BAL_ID` varchar(9) NOT NULL,
          `CAND_ID` varchar(9) NOT NULL,
          `SUP_OFF_CD` varchar(1) NOT NULL,
          `SUP_OPP_CD` varchar(1) NOT NULL,
          `IS_DUPLICATE` bool
        )
        """ % dict(
            tmp_table=self.late_tmp_table,
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
                `AMEND_ID`,
                `LINE_ITEM`,
                `REC_TYPE`,
                `FORM_TYPE`,
                `TRAN_ID`,
                `ENTITY_CD`,
                `ENTY_NAML`,
                `ENTY_NAMF`,
                `ENTY_NAMT`,
                `ENTY_NAMS`,
                `ENTY_CITY`,
                `ENTY_ST`,
                `ENTY_ZIP4`,
                `CTRIB_EMP`,
                `CTRIB_OCC`,
                `CTRIB_SELF`,
                `ELEC_DATE`,
                `CTRIB_DATE`,
                `DATE_THRU`,
                `AMOUNT`,
                `CMTE_ID`,
                `CAND_NAML`,
                `CAND_NAMF`,
                `CAND_NAMT`,
                `CAND_NAMS`,
                `OFFICE_CD`,
                `OFFIC_DSCR`,
                `JURIS_CD`,
                `JURIS_DSCR`,
                `DIST_NO`,
                `OFF_S_H_CD`,
                `BAL_NAME`,
                `BAL_NUM`,
                `BAL_JURIS`,
                `MEMO_CODE`,
                `MEMO_REFNO`,
                `BAL_ID`,
                `CAND_ID`,
                `SUP_OFF_CD`,
                `SUP_OPP_CD`,
                `IS_DUPLICATE`
            )
        """ % dict(
            tmp_table=self.late_tmp_table,
            target_csv=self.late_target_csv,
        )
        self.cursor.execute(sql)

        self.log("  Merging CSV data with other tables")
        sql = """
            INSERT INTO %(contribs_model)s (
                cycle_id,
                committee_id,
                filing_id,
                filing_id_raw,
                transaction_id,
                amend_id,
                is_duplicate,
                date_received,
                amount,
                contributor_full_name,
                contributor_is_person,
                contributor_committee_id,
                contributor_prefix,
                contributor_first_name,
                contributor_last_name,
                contributor_suffix,
                contributor_city,
                contributor_state,
                contributor_zipcode,
                contributor_occupation,
                contributor_employer,
                contributor_selfemployed,
                contributor_entity_type
            )
            SELECT
                f.cycle_id as cycle_id,
                f.committee_id as committee_id,
                f.id as filing_id,
                f.filing_id_raw,
                r.tran_id,
                r.amend_id,
                r.is_duplicate,
                r.ctrib_date,
                r.amount,
                CASE
                    WHEN r.enty_namf <> '' THEN r.ctrib_emp
                    ELSE r.enty_naml
                END as contributor_full_name,
                CASE
                    WHEN r.enty_namf <> '' THEN true
                    ELSE false
                END as contributor_is_person,
                c.id,
                r.enty_namt,
                r.enty_namf,
                r.enty_naml,
                r.enty_nams,
                r.enty_city,
                r.enty_st,
                r.enty_zip4,
                r.ctrib_occ,
                r.ctrib_emp,
                r.ctrib_self,
                r.entity_cd
            FROM %(filing_model)s as f
            INNER JOIN %(raw_model)s as r
            ON f.filing_id_raw = r.filing_id
            AND f.amend_id = r.amend_id
            LEFT OUTER JOIN %(committee_model)s as c
            ON r.cmte_id = c.xref_filer_id
            WHERE r.`FORM_TYPE` = 'F497P1'
        """ % dict(
            contribs_model=Contribution._meta.db_table,
            filing_model=Filing._meta.db_table,
            raw_model=self.late_tmp_table,
            committee_model=Committee._meta.db_table,
        )
        self.cursor.execute(sql)
        self.cursor.execute("DROP TABLE %s" % self.late_tmp_table)

    def transform_quarterly_contributions_csv(self):
        self.log("  Marking duplicates")
        self.log("   Dumping CSV sorted by unique identifier")
        sql = """
        SELECT
            `FILING_ID`,
            `AMEND_ID`,
            `LINE_ITEM`,
            `REC_TYPE`,
            `FORM_TYPE`,
            `TRAN_ID`,
            `ENTITY_CD`,
            `CTRIB_NAML`,
            `CTRIB_NAMF`,
            `CTRIB_NAMT`,
            `CTRIB_NAMS`,
            `CTRIB_CITY`,
            `CTRIB_ST`,
            `CTRIB_ZIP4`,
            `CTRIB_EMP`,
            `CTRIB_OCC`,
            `CTRIB_SELF`,
            `TRAN_TYPE`,
            `RCPT_DATE`,
            `DATE_THRU`,
            `AMOUNT`,
            `CUM_YTD`,
            `CUM_OTH`,
            `CTRIB_DSCR`,
            `CMTE_ID`,
            `TRES_NAML`,
            `TRES_NAMF`,
            `TRES_NAMT`,
            `TRES_NAMS`,
            `TRES_CITY`,
            `TRES_ST`,
            `TRES_ZIP4`,
            `INTR_NAML`,
            `INTR_NAMF`,
            `INTR_NAMT`,
            `INTR_NAMS`,
            `INTR_CITY`,
            `INTR_ST`,
            `INTR_ZIP4`,
            `INTR_EMP`,
            `INTR_OCC`,
            `INTR_SELF`,
            `CAND_NAML`,
            `CAND_NAMF`,
            `CAND_NAMT`,
            `CAND_NAMS`,
            `OFFICE_CD`,
            `OFFIC_DSCR`,
            `JURIS_CD`,
            `JURIS_DSCR`,
            `DIST_NO`,
            `OFF_S_H_CD`,
            `BAL_NAME`,
            `BAL_NUM`,
            `BAL_JURIS`,
            `SUP_OPP_CD`,
            `MEMO_CODE`,
            `MEMO_REFNO`,
            `BAKREF_TID`,
            `XREF_SCHNM`,
            `XREF_MATCH`,
            `INT_RATE`,
            `INTR_CMTEID`
        FROM %(raw_model)s
        ORDER BY FILING_ID, TRAN_ID, AMEND_ID DESC
        INTO OUTFILE '%(tmp_csv)s'
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\n'
        """ % dict(
            raw_model=RcptCd._meta.db_table,
            tmp_csv=self.quarterly_tmp_csv,
        )
        self.cursor.execute(sql)

        INHEADERS = [
            "FILING_ID",
            "AMEND_ID",
            "LINE_ITEM",
            "REC_TYPE",
            "FORM_TYPE",
            "TRAN_ID",
            "ENTITY_CD",
            "CTRIB_NAML",
            "CTRIB_NAMF",
            "CTRIB_NAMT",
            "CTRIB_NAMS",
            "CTRIB_CITY",
            "CTRIB_ST",
            "CTRIB_ZIP4",
            "CTRIB_EMP",
            "CTRIB_OCC",
            "CTRIB_SELF",
            "TRAN_TYPE",
            "RCPT_DATE",
            "DATE_THRU",
            "AMOUNT",
            "CUM_YTD",
            "CUM_OTH",
            "CTRIB_DSCR",
            "CMTE_ID",
            "TRES_NAML",
            "TRES_NAMF",
            "TRES_NAMT",
            "TRES_NAMS",
            "TRES_CITY",
            "TRES_ST",
            "TRES_ZIP4",
            "INTR_NAML",
            "INTR_NAMF",
            "INTR_NAMT",
            "INTR_NAMS",
            "INTR_CITY",
            "INTR_ST",
            "INTR_ZIP4",
            "INTR_EMP",
            "INTR_OCC",
            "INTR_SELF",
            "CAND_NAML",
            "CAND_NAMF",
            "CAND_NAMT",
            "CAND_NAMS",
            "OFFICE_CD",
            "OFFIC_DSCR",
            "JURIS_CD",
            "JURIS_DSCR",
            "DIST_NO",
            "OFF_S_H_CD",
            "BAL_NAME",
            "BAL_NUM",
            "BAL_JURIS",
            "SUP_OPP_CD",
            "MEMO_CODE",
            "MEMO_REFNO",
            "BAKREF_TID",
            "XREF_SCHNM",
            "XREF_MATCH",
            "INT_RATE",
            "INTR_CMTEID"
        ]
        OUTHEADERS = copy.copy(INHEADERS)
        OUTHEADERS.append("IS_DUPLICATE")

        self.log("   Marking duplicates in a new CSV")
        with open(self.quarterly_tmp_csv, 'r') as fin:
            fout = csv.DictWriter(
                open(self.quarterly_target_csv, 'wb'),
                fieldnames=OUTHEADERS
            )
            fout.writeheader()
            last_uid = ''
            for r in csv.DictReader(fin, fieldnames=INHEADERS):
                r.pop(None, None)
                uid = '%s-%s' % (r['FILING_ID'], r['TRAN_ID'])
                if uid != last_uid:
                    r['IS_DUPLICATE'] = 0
                    last_uid = uid
                else:
                    r['IS_DUPLICATE'] = 1
                try:
                    fout.writerow(r)
                except ValueError:
                    continue

    def load_quarterly_contributions(self):
        self.log("  Loading CSV")
        self.cursor.execute("DROP TABLE IF EXISTS TMP_RCPT_CD;")
        sql = """
        CREATE TABLE `TMP_RCPT_CD` (
          `AMEND_ID` int(11),
          `AMOUNT` decimal(14,2),
          `BAKREF_TID` varchar(20),
          `BAL_JURIS` varchar(40),
          `BAL_NAME` varchar(200),
          `BAL_NUM` varchar(7),
          `CAND_NAMF` varchar(45),
          `CAND_NAML` varchar(200),
          `CAND_NAMS` varchar(10),
          `CAND_NAMT` varchar(10),
          `CMTE_ID` varchar(9),
          `CTRIB_ADR1` varchar(55),
          `CTRIB_ADR2` varchar(55),
          `CTRIB_CITY` varchar(30),
          `CTRIB_DSCR` varchar(90),
          `CTRIB_EMP` varchar(200),
          `CTRIB_NAMF` varchar(45),
          `CTRIB_NAML` varchar(200),
          `CTRIB_NAMS` varchar(10),
          `CTRIB_NAMT` varchar(10),
          `CTRIB_OCC` varchar(60),
          `CTRIB_SELF` varchar(1),
          `CTRIB_ST` varchar(2),
          `CTRIB_ZIP4` varchar(10),
          `CUM_OTH` decimal(14,2) DEFAULT NULL,
          `CUM_YTD` decimal(14,2) DEFAULT NULL,
          `DATE_THRU` date DEFAULT NULL,
          `DIST_NO` varchar(3),
          `ENTITY_CD` varchar(3),
          `FILING_ID` int(11),
          `FORM_TYPE` varchar(9),
          `INT_RATE` varchar(9),
          `INTR_ADR1` varchar(55),
          `INTR_ADR2` varchar(55),
          `INTR_CITY` varchar(30),
          `INTR_CMTEID` varchar(9),
          `INTR_EMP` varchar(200),
          `INTR_NAMF` varchar(45),
          `INTR_NAML` varchar(200),
          `INTR_NAMS` varchar(10),
          `INTR_NAMT` varchar(10),
          `INTR_OCC` varchar(60),
          `INTR_SELF` varchar(1),
          `INTR_ST` varchar(2),
          `INTR_ZIP4` varchar(10),
          `JURIS_CD` varchar(3),
          `JURIS_DSCR` varchar(40),
          `LINE_ITEM` int(11),
          `MEMO_CODE` varchar(1),
          `MEMO_REFNO` varchar(20),
          `OFF_S_H_CD` varchar(1),
          `OFFIC_DSCR` varchar(40),
          `OFFICE_CD` varchar(3),
          `RCPT_DATE` date,
          `REC_TYPE` varchar(4),
          `SUP_OPP_CD` varchar(1),
          `TRAN_ID` varchar(20),
          `TRAN_TYPE` varchar(1),
          `TRES_ADR1` varchar(55),
          `TRES_ADR2` varchar(55),
          `TRES_CITY` varchar(30),
          `TRES_NAMF` varchar(45),
          `TRES_NAML` varchar(200),
          `TRES_NAMS` varchar(10),
          `TRES_NAMT` varchar(10),
          `TRES_ST` varchar(2),
          `TRES_ZIP4` int(11) DEFAULT NULL,
          `XREF_MATCH` varchar(1),
          `XREF_SCHNM` varchar(2),
          `IS_DUPLICATE` bool
        )
        """
        self.cursor.execute(sql)

        sql = """
            LOAD DATA LOCAL INFILE '%s'
            INTO TABLE TMP_RCPT_CD
            FIELDS TERMINATED BY ','
            OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\\n'
            IGNORE 1 LINES (
            `FILING_ID`,
            `AMEND_ID`,
            `LINE_ITEM`,
            `REC_TYPE`,
            `FORM_TYPE`,
            `TRAN_ID`,
            `ENTITY_CD`,
            `CTRIB_NAML`,
            `CTRIB_NAMF`,
            `CTRIB_NAMT`,
            `CTRIB_NAMS`,
            `CTRIB_CITY`,
            `CTRIB_ST`,
            `CTRIB_ZIP4`,
            `CTRIB_EMP`,
            `CTRIB_OCC`,
            `CTRIB_SELF`,
            `TRAN_TYPE`,
            `RCPT_DATE`,
            `DATE_THRU`,
            `AMOUNT`,
            `CUM_YTD`,
            `CUM_OTH`,
            `CTRIB_DSCR`,
            `CMTE_ID`,
            `TRES_NAML`,
            `TRES_NAMF`,
            `TRES_NAMT`,
            `TRES_NAMS`,
            `TRES_CITY`,
            `TRES_ST`,
            `TRES_ZIP4`,
            `INTR_NAML`,
            `INTR_NAMF`,
            `INTR_NAMT`,
            `INTR_NAMS`,
            `INTR_CITY`,
            `INTR_ST`,
            `INTR_ZIP4`,
            `INTR_EMP`,
            `INTR_OCC`,
            `INTR_SELF`,
            `CAND_NAML`,
            `CAND_NAMF`,
            `CAND_NAMT`,
            `CAND_NAMS`,
            `OFFICE_CD`,
            `OFFIC_DSCR`,
            `JURIS_CD`,
            `JURIS_DSCR`,
            `DIST_NO`,
            `OFF_S_H_CD`,
            `BAL_NAME`,
            `BAL_NUM`,
            `BAL_JURIS`,
            `SUP_OPP_CD`,
            `MEMO_CODE`,
            `MEMO_REFNO`,
            `BAKREF_TID`,
            `XREF_SCHNM`,
            `XREF_MATCH`,
            `INT_RATE`,
            `INTR_CMTEID`,
            `IS_DUPLICATE`
            )
        """ % (
            self.quarterly_target_csv,
        )
        self.cursor.execute(sql)

        self.log("  Merging CSV data with other tables")
        sql = """
            INSERT INTO %(contribs_model)s (
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
                transaction_type,
                date_received,
                contribution_description,
                amount,
                contributor_full_name,
                contributor_is_person,
                contributor_committee_id,
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
                contributor_entity_type,
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
                f.filing_id_raw,
                r.tran_id,
                r.amend_id,
                r.bakref_tid,
                r.xref_match,
                r.xref_schnm,
                r.is_duplicate,
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
                c.id,
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
                r.entity_cd,
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
            LEFT OUTER JOIN %(committee_model)s as c
            ON r.cmte_id = c.xref_filer_id
        """ % dict(
            contribs_model=Contribution._meta.db_table,
            filing_model=Filing._meta.db_table,
            raw_model="TMP_RCPT_CD",
            committee_model=Committee._meta.db_table,
        )
        self.cursor.execute(sql)
        self.cursor.execute("DROP TABLE TMP_RCPT_CD;")
