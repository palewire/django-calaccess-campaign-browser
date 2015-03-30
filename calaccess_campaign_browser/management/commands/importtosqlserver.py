import os
import re
import csv
import fnmatch
import datetime
from optparse import make_option

import pypyodbc
from ipdb import set_trace as debugger

from django.conf import settings
from django.db import connection
from django.db.models import get_model
from django.core.management.base import AppCommand

from calaccess_campaign_browser.management.commands import CalAccessCommand

custom_options = (
    make_option(
        "--skip-contributions",
        action="store_false",
        dest="contributions",
        default=True,
        help="Skip contributions import"
    ),
    make_option(
        "--skip-expenditures",
        action="store_false",
        dest="expenditures",
        default=True,
        help="Skip expenditures import"
    ),
    make_option(
        "--skip-summary",
        action="store_false",
        dest="summary",
        default=True,
        help="Skip summary import"
    ),
)

def all_files(root, patterns='*', single_level=False, yield_folders=False):
    """
    Expand patterns form semicolon-separated string to list
    example usage: thefiles = list(all_files('/tmp', '*.py;*.htm;*.html'))
    """
    patterns = patterns.split(';')

    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)

        files.sort()

        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break

        if single_level:
            break

class Command(CalAccessCommand):
    """
    Send CSVs exported from `exportcalaccesscampaignbrowser` to
    Microsoft SQL Server
    """
    option_list = CalAccessCommand.option_list + custom_options
    conn_path = (
        'Driver=%s;Server=%s;port=%s;uid=%s;pwd=%s;database=%s;autocommit=1'
    ) % (
        settings.SQL_SERVER_DRIVER,
        settings.SQL_SERVER_ADDRESS,
        settings.SQL_SERVER_PORT,
        settings.SQL_SERVER_USER,
        settings.SQL_SERVER_PASSWORD,
        settings.SQL_SERVER_DATABASE
    )

    conn = pypyodbc.connect(conn_path)
    cursor = conn.cursor()
    app = AppCommand()

    def set_options(self, *args, **kwargs):
        self.data_dir = os.path.join(
            settings.BASE_DIR, 'data')
        os.path.exists(self.data_dir) or os.mkdir(self.data_dir)

    def generate_table_schema(self, model_name):
        """
        Take Expenditure, Contribution or Summary models; grab their db schema,
        and create MS SQL Server compatible schema
        """
        self.log('  Creating database schema for {} ...'.format(model_name))
        style = self.app.style
        today = datetime.datetime.today()

        model = get_model('calaccess_campaign_browser', model_name)

        table_name = 'dbo.{}'.format(model._meta.db_table)

        fieldnames = [f.name for f in model._meta.fields] + [
            'committee_name', 'filer_name', 'filer_id', 'filer_id_raw']

        raw_statement = connection.creation\
            .sql_create_model(model, style)[0][0]

        # http://stackoverflow.com/a/14693789/868724
        ansi_escape = re.compile(r'\x1b[^m]*m')
        strip_ansi_statement = (ansi_escape.sub('', raw_statement))
        statement = strip_ansi_statement.replace('\n', '')\
            .replace('`','')\
            .replace('bool', 'bit')\
            .replace(' AUTO_INCREMENT', '')\
            .replace(model._meta.db_table, table_name)\
            .replace('NOT NULL', '')

        statement = """{}, committee_name varchar(255),\
            filer_name varchar(255), filer_id integer,\
            filer_id_raw integer );""".format(statement[:-3])

        self.construct_table(model_name, table_name, statement)

    def construct_table(self, model_name, table_name, query):
        """
        Create matching MS SQL Server database table
        """
        statement = str(query)
        self.log('  Creating {} table ...'.format(table_name))
        drop_path = "IF object_id('{}') IS NOT NULL DROP TABLE {}".format(
            table_name, table_name)

        self.cursor.execute(drop_path)
        self.cursor.execute(statement)
        self.cursor.commit()

        self.success('    {} created'.format(table_name))

        self.load_table(table_name, model_name)

    def load_table(self, table_name, model_name):
        """
        Load Table with CSVs generated from `exportcalaccesscampaignbrowser`
        See: https://msdn.microsoft.com/en-us/library/ms188609.aspx
        """
        self.log('  Loading table {} ...'.format(table_name))
        all_csvs = list(all_files(self.data_dir, '*.csv'))

        csv_ = [f for f in all_csvs if fnmatch.fnmatch(f, '*-{}.csv'.format(
            model_name))]

        if len(csv_) > 1:
            self.log('  There are multiple files matching {}'.format(
                model_name))
            self.log('  We only support one match at the moment. Sorry!')

            raise NotImplementedError

        with open(csv_[0]) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            reader.next()  # skip headers

            for row in reader:
                # Remove none values and turn booleans into bit type
                row = [r.replace('"', '') for r in row]
                row = [r.replace('None', '') for r in row]
                row = [r.replace('True', '0') for r in row]
                row = [r.replace('False', '1') for r in row]

                sql = """INSERT INTO {} VALUES {};""".format(
                    table_name, tuple(row))

                try:
                    self.cursor.execute(sql)
                    self.log('      loading {} ID:{} ...'.format(
                        model_name, row[0]))
                except pypyodbc.Error, e:
                    debugger()

            self.cursor.commit()
            self.success('    Loaded {} with data from {}'.format(
                table_name, os.path.split(csv_[0])[1]))

    def handle(self, *args, **options):
        self.header('Importing models ...')
        self.set_options(*args, **options)

        if options['contributions']:
            self.generate_table_schema('contribution')

        if options['expenditures']:
            self.generate_table_schema('expenditure')
