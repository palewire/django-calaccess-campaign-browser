import os
import csv
import datetime
from optparse import make_option

from django.conf import settings
from django.db.models import get_model
from calaccess_campaign_browser.management.commands import CalAccessCommand

from calaccess_campaign_browser.models import Cycle

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


class Command(CalAccessCommand):
    help = 'Export refined CAL-ACCESS campaign browser data as CSV files'
    option_list = CalAccessCommand.option_list + custom_options

    def set_options(self, *args, **kwargs):
        self.data_dir = os.path.join(
            settings.BASE_DIR, 'data')
        os.path.exists(self.data_dir) or os.mkdir(self.data_dir)

    def encoded(self, list_of_lists):
        """
        Take a list of lists, and encode each list item as utf-8
        http://stackoverflow.com/a/17527101/868724
        """
        return [[unicode(s).encode('utf-8') for s in t] for t in list_of_lists]

    def export_to_csv(self, model_name):
        self.header('Exporting models ...')

        today = datetime.datetime.today()
        model = get_model('calaccess_campaign_browser', model_name)

        fieldnames = [f.name for f in model._meta.fields] + [
            'committee_name', 'filer_name', 'filer_id', 'filer_id_raw']

        relation_names = [f.name for f in model._meta.fields] + [
            'committee__name',
            'committee__filer__name',
            'committee__filer__id',
            'committee__filer__filer_id_raw'
        ]

        filename = '{}-{}-{}-{}.csv'.format(
            today.year,
            today.month,
            today.day,
            model_name.lower()
        )
        filepath = os.path.join(self.data_dir, filename)

        self.header('  Exporting {} model ...'.format(model_name.capitalize()))

        with open(filepath, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter="\t")
            writer.writerow(fieldnames)

            if model_name != 'summary':
                for cycle in Cycle.objects.all():
                    self.log('    Looking at cycle {} ...'.format(cycle.name))
                    rows = model.objects.filter(cycle=cycle)\
                        .exclude(is_duplicate=True)\
                        .values_list(*relation_names)

                    if not rows:
                        self.failure('      No data for {}'.format(cycle.name))

                    else:
                        rows = self.encoded(rows)
                        writer.writerows(rows)
                        self.success('      Added {} {} data'.format(
                            cycle.name, model_name))
            else:
                rows = self.encoded(model.objects.values_list())
                writer.writerows(rows)

        self.success('  Exported {}!'.format(model_name.capitalize()))

    def handle(self, *args, **options):
        self.set_options(*args, **options)

        if options['contributions']:
            self.export_to_csv('contribution')

        if options['expenditures']:
            self.export_to_csv('expenditure')

        if options['summary']:
            self.export_to_csv('summary')
