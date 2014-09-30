import os
import csv
import copy
import tempfile
from django.db import connection
from calaccess_raw.models import RcptCd
from calaccess_raw import get_download_directory
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.models import Contribution, Filing, Committee


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.data_dir = os.path.join(get_download_directory(), 'csv')
        self.source_csv = os.path.join(self.data_dir, 'rcpt_cd.csv')
        self.tmp_csv = tempfile.NamedTemporaryFile().name
        self.target_csv = os.path.join(
            self.data_dir,
            'rcpt_cd_transformed.csv'
        )
        self.transform_csv()
        self.load_contributions()

    def transform_csv(self):
        print "- Marking duplicates"

        print "-- Outputing CSV dump sorted by unique identifier"
        c = connection.cursor()
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
            tmp_csv=self.tmp_csv,
        )
        c.execute(sql)

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

        print "-- Marking duplicates in a new CSV"
        with open(self.tmp_csv,'r') as fin:
            fout = csv.DictWriter(
                open(self.target_csv, 'wb'),
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

    def load_contributions(self):
        print "- Loading contributions"
        c = connection.cursor()
        sql = """
        CREATE TABLE `RCPT_CD_TMP` (
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
        c.execute(sql)

        sql = """
            LOAD DATA LOCAL INFILE '%s'
            INTO TABLE RCPT_CD_TMP
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
            self.target_csv,
        )
        c.execute(sql)
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
            raw_model=RcptCd._meta.db_table + "_TMP",
            committee_model=Committee._meta.db_table,
        )
        c.execute(sql)
        c.execute("DROP TABLE RCPT_CD_TMP")
