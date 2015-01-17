from optparse import make_option
import os
import csvkit

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.datastructures import SortedDict

from calaccess_campaign_browser.models import (
    Contribution,
    Cycle,
    Expenditure,
    Summary
)

custom_options = (
    make_option(
        "--skip-contributions",
        action="store_false",
        dest="contributions",
        default=True,
        help="Skip contributions export"
    ),
    make_option(
        "--skip-expenditures",
        action="store_false",
        dest="expenditures",
        default=True,
        help="Skip expenditures export"
    ),
    make_option(
        "--skip-summary",
        action="store_false",
        dest="summary",
        default=True,
        help="Skip summary export"
    ),
)


class Command(BaseCommand):
    help = 'Export refined CAL-ACCESS campaign browser data as CSV files'
    option_list = BaseCommand.option_list + custom_options

    def set_options(self, *args, **kwargs):
        self.data_dir = os.path.join(
            settings.BASE_DIR, 'data')
        os.path.exists(self.data_dir) or os.mkdir(self.data_dir)

    def handle(self, *args, **options):
        self.set_options(*args, **options)
        if options['contributions']:
            self.contributions()
        if options['expenditures']:
            self.expenditures()
        if options['summary']:
            self.summary()

    def contributions(self):
        print 'working on contributions'
        csv_name = 'contributions.csv'
        outfile_path = os.path.join(self.data_dir,  csv_name)
        outfile = open(outfile_path, 'w')

        header_translation = SortedDict([
            ('amount', 'amount'),
            ('bakref_tid', 'bakref_tid'),
            ('cmte_id', 'cmte_id'),
            ('committee__filer__name', 'filer'),
            ('committee__filer__filer_id', 'filer_id'),
            ('committee__name', 'committee'),
            ('committee__filer_id_raw', 'committee_id'),
            ('ctrib_adr1', 'ctrib_adr1'),
            ('ctrib_adr2', 'ctrib_adr2'),
            ('ctrib_city', 'ctrib_city'),
            ('ctrib_dscr', 'ctrib_dscr'),
            ('ctrib_emp', 'ctrib_emp'),
            ('ctrib_namf', 'ctrib_namf'),
            ('ctrib_naml', 'ctrib_naml'),
            ('ctrib_nams', 'ctrib_nams'),
            ('ctrib_namt', 'ctrib_namt'),
            ('ctrib_occ', 'ctrib_occ'),
            ('ctrib_self', 'ctrib_self'),
            ('ctrib_st', 'ctrib_st'),
            ('ctrib_zip4', 'ctrib_zip4'),
            ('cum_oth', 'cum_oth'),
            ('cum_ytd', 'cum_ytd'),
            ('cycle__name', 'cycle'),
            ('date_thru', 'date_thru'),
            ('entity_cd', 'entity_cd'),
            ('filing__filing_id_raw', 'filing_id'),
            ('filing__start_date', 'filing_start_date'),
            ('filing__end_date', 'filing_end_date'),
            ('form_type', 'form_type'),
            ('id', 'id'),
            ('intr_adr1', 'intr_adr1'),
            ('intr_adr2', 'intr_adr2'),
            ('intr_city', 'intr_city'),
            ('intr_cmteid', 'intr_cmteid'),
            ('intr_emp', 'intr_emp'),
            ('intr_namf', 'intr_namf'),
            ('intr_naml', 'intr_naml'),
            ('intr_nams', 'intr_nams'),
            ('intr_namt', 'intr_namt'),
            ('intr_occ', 'intr_occ'),
            ('intr_self', 'intr_self'),
            ('intr_st', 'intr_st'),
            ('intr_zip4', 'intr_zip4'),
            ('line_item', 'line_item'),
            ('memo_code', 'memo_code'),
            ('memo_refno', 'memo_refno'),
            ('raw_org_name', 'raw_org_name'),
            ('rcpt_date', 'rcpt_date'),
            ('rec_type', 'rec_type'),
            ('tran_id', 'tran_id'),
            ('tran_type', 'tran_type'),
            ('xref_match', 'xref_match'),
            ('xref_schnm', 'xref_schnm'),
        ])
        csv_writer = csvkit.unicsv.UnicodeCSVDictWriter(
            outfile, fieldnames=header_translation.keys(), delimiter='|')
        csv_writer.writerow(header_translation)
        for c in Cycle.objects.all():
            dict_rows = Contribution.objects.filter(cycle=c).exclude(
                dupe=True).values(*header_translation.keys())
            csv_writer.writerows(dict_rows)
        outfile.close()
        print 'Exported contributions'

    def expenditures(self):
        print 'working on expenditures'
        csv_name = 'expenditures.csv'
        outfile_path = os.path.join(self.data_dir,  csv_name)
        outfile = open(outfile_path, 'w')

        header_translation = SortedDict([
            ('amount', 'amount'),
            ('bakref_tid', 'bakref_tid'),
            ('cmte_id', 'cmte_id'),
            ('committee__filer__name', 'filer'),
            ('committee__filer__filer_id', 'filer_id'),
            ('committee__name', 'committee'),
            ('committee__filer_id_raw', 'committee_id'),
            ('cum_ytd', 'cum_ytd'),
            ('cycle__name', 'cycle'),
            ('entity_cd', 'entity_cd'),
            ('expn_chkno', 'expn_chkno'),
            ('expn_code', 'expn_code'),
            ('expn_date', 'expn_date'),
            ('expn_dscr', 'expn_dscr'),
            ('filing__filing_id_raw', 'filing_id'),
            ('filing__start_date', 'filing_start_date'),
            ('filing__end_date', 'filing_end_date'),
            ('form_type', 'form_type'),
            ('g_from_e_f', 'g_from_e_f'),
            ('id', 'id'),
            ('individual_id', 'individual_id'),
            ('line_item', 'line_item'),
            ('memo_code', 'memo_code'),
            ('memo_refno', 'memo_refno'),
            ('name', 'name'),
            ('org_id', 'org_id'),
            ('payee_adr1', 'payee_adr1'),
            ('payee_adr2', 'payee_adr2'),
            ('payee_city', 'payee_city'),
            ('payee_namf', 'payee_namf'),
            ('payee_naml', 'payee_naml'),
            ('payee_nams', 'payee_nams'),
            ('payee_namt', 'payee_namt'),
            ('payee_st', 'payee_st'),
            ('payee_zip4', 'payee_zip4'),
            ('tran_id', 'tran_id'),
            ('xref_match', 'xref_match'),
            ('xref_schnm', 'xref_schnm'),
        ])
        csv_writer = csvkit.unicsv.UnicodeCSVDictWriter(
            outfile, fieldnames=header_translation.keys(), delimiter='|')
        csv_writer.writerow(header_translation)
        for c in Cycle.objects.all():
            dict_rows = Expenditure.objects.filter(cycle=c).exclude(
                dupe=True).values(*header_translation.keys())
            csv_writer.writerows(dict_rows)
        outfile.close()
        print 'Exported expenditures '

    def summary(self):
        print 'working on summary'
        csv_name = 'summary.csv'
        outfile_path = os.path.join(self.data_dir,  csv_name)
        outfile = open(outfile_path, 'w')

        header_translation = SortedDict([
            ('committee__filer__name', 'filer'),
            ('committee__filer__filer_id', 'filer_id'),
            ('committee__name', 'committee'),
            ('committee__filer_id_raw', 'committee_id'),
            ('cycle__name', 'cycle'),
            ('ending_cash_balance', 'ending_cash_balance'),
            ('filing__filing_id_raw', 'filing_id'),
            ('filing__start_date', 'filing_start_date'),
            ('filing__end_date', 'filing_end_date'),
            ('form_type', 'form_type'),
            ('id', 'id'),
            ('itemized_expenditures', 'itemized_expenditures'),
            (
                'itemized_monetary_contributions',
                'itemized_monetary_contributions'
            ),
            ('non_monetary_contributions', 'non_monetary_contributions'),
            ('outstanding_debts', 'outstanding_debts'),
            ('total_contributions', 'total_contributions'),
            ('total_expenditures', 'total_expenditures'),
            ('total_monetary_contributions', 'total_monetary_contributions'),
            ('unitemized_expenditures', 'unitemized_expenditures'),
            (
                'unitemized_monetary_contributions',
                'unitemized_monetary_contributions'
            ),
        ])
        csv_writer = csvkit.unicsv.UnicodeCSVDictWriter(
            outfile, fieldnames=header_translation.keys(), delimiter='|')
        csv_writer.writerow(header_translation)
        for c in Cycle.objects.all():
            dict_rows = Summary.objects.filter(cycle=c).exclude(
                dupe=True).values(*header_translation.keys())
            csv_writer.writerows(dict_rows)
        outfile.close()
        print 'Exported summary'
