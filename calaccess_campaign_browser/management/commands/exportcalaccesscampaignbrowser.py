import os
import csvkit
from optparse import make_option
from collections import OrderedDict

from django.conf import settings
from django.core.management.base import BaseCommand

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

contributions_header = OrderedDict([
    ('amount', 'amount'),
    ('filing_id', 'filing_id'),
    ('committee__name', 'committee_name'),
    ('cycle_id', 'cycle'),
    ('date_received', 'date_received'),
    ('contributor_first_name', 'contributor_first_name'),
    ('contributor_last_name', 'contributor_last_name'),
    ('contributor_full_name', 'contributor_full_name'),
    ('contributor_occupation', 'contributor_occupation'),
    ('contributor_employer', 'contributor_employer'),
    ('contributor_address_1', 'contributor_address_1'),
    ('contributor_address_2', 'contributor_address_2'),
    ('contributor_city', 'contributor_city'),
    ('contributor_state', 'contributor_state'),
    ('contributor_zipcode', 'contributor_zipcode'),
])
expenditures_header = OrderedDict([
    ('amount', 'amount'),
    ('filing_id', 'filing_id'),
    ('committee__name', 'committee_name'),
    ('cycle_id', 'cycle'),
    ('expn_date', 'date_received'),
    ('payee_namf', 'payee_first_name'),
    ('payee_naml', 'payee_last_name'),
    ('name', 'payee_full_name'),
    ('payee_namt', 'payee_occupation'),
    ('raw_org_name', 'payee_employer'),
    ('payee_adr1', 'payee_address_1'),
    ('payee_adr2', 'payee_address_2'),
    ('payee_city', 'payee_city'),
    ('payee_st', 'payee_state'),
    ('payee_zip4', 'payee_zipcode'),
])
summary_header = OrderedDict([
    # ('committee__filer__name', 'filer'),
    # ('committee__filer__filer_id', 'filer_id'),
    # ('committee__name', 'committee'),
    # ('committee__filer_id_raw', 'committee_id'),
    # ('cycle__name', 'cycle'),
    ('ending_cash_balance', 'ending_cash_balance'),
    ('filing_id_raw', 'filing_id'),
    ('amend_id', 'amend_id'),
    # ('filing__start_date', 'filing_start_date'),
    # ('filing__end_date', 'filing_end_date'),
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
            self.export_to_csv('contributions', contributions_header)
        if options['expenditures']:
            self.export_to_csv('expenditures', expenditures_header)
        if options['summary']:
            self.export_to_csv('summary', summary_header)

    def export_to_csv(self, outfile_name, header_translation):
        print 'working on %s' % outfile_name
        csv_name = '%s.csv' % outfile_name
        outfile_path = os.path.join(self.data_dir,  csv_name)
        outfile = open(outfile_path, 'w')

        csv_writer = csvkit.unicsv.UnicodeCSVDictWriter(
            outfile, fieldnames=header_translation.keys(), delimiter=',')

        csv_writer.writerow(header_translation)

        for c in Cycle.objects.all():
            if outfile_name == 'contributions':
                dict_rows = Contribution.objects.filter(cycle=c).exclude(
                    is_duplicate=True).values(*header_translation.keys())
                csv_writer.writerows(dict_rows)

            elif outfile_name == 'expenditures':
                dict_rows = Expenditure.objects.filter(cycle=c).exclude(
                    dupe=True).values(*header_translation.keys())
                csv_writer.writerows(dict_rows)

            elif outfile_name == 'summary':
                pass

            else:
                print("You did not specify 'contributions, \
                    'expenditures' or 'summary'. Exiting")
                raise

        # Summary specific
        if outfile_name == 'summary':
            rows = Summary.objects.all().values(*header_translation.keys())
            csv_writer.writerows(rows)

        outfile.close()

        print('Exported %s' % outfile_name)
