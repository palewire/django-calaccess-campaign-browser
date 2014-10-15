import os
import csv
from optparse import make_option

import pypyodbc

from django.conf import settings
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.management.commands.exportcalaccesscampaignfinance import (
    expenditures_header,
    contributions_header,
    summary_header
)

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


class Command(BaseCommand):
    help = 'descriptive text'
    option_list = BaseCommand.option_list + custom_options
    connection_path = (
        'Driver=%s;Server=%s;port=%s;uid=%s;pwd=%s;database=%s;autocommit=1'
    ) % (
        settings.SQL_SERVER_DRIVER,
        settings.SQL_SERVER_ADDRESS,
        settings.SQL_SERVER_PORT,
        settings.SQL_SERVER_USER,
        settings.SQL_SERVER_PASSWORD,
        settings.SQL_SERVER_DATABASE
    )

    connection = pypyodbc.connect(connection_path)

    cursor = connection.cursor()

    def handle(self, *args, **options):
        sql_contributions = '''
            CREATE TABLE [dbo].[new_contributions] (
                [amount] decimal(14,2),
                [filing_id] int,
                [committee_name] nvarchar(600),
                [cycle] int,
                [date_received] date,
                [contributor_first_name] nvarchar(255),
                [contributor_last_name] nvarchar(600),
                [contributor_full_name] nvarchar(50),
                [contributor_occupation] nvarchar(50),
                [contributor_employer] nvarchar(60),
                [contributor_address_1] nvarchar(55),
                [contributor_address_2] nvarchar(55),
                [contributor_city] nvarchar(50),
                [contributor_state] nvarchar(90),
                [contributor_zipcode] nvarchar(200)
        )
        '''

        sql_expenditures = '''
            CREATE TABLE [dbo].[new_expenditures] (
                [amount] decimal(14,2),
                [filing_id] int,
                [committee_name] nvarchar(600),
                [cycle] int,
                [date_received] date,
                [payee_first_name] nvarchar(255)
                [payee_last_name] nvarchar(600)
                [payee_full_name] nvarchar(50)
                [payee_occupation] nvarchar(50)
                [payee_employer] nvarchar(60)
                [payee_address_1] nvarchar(55)
                [payee_address_2] nvarchar(55)
                [payee_city] nvarchar(50)
                [payee_state] nvarchar(90)
                [payee_zipcode] nvarchar(200)
            )
        '''

        if options['contributions']:
            self.construct_tables('contributions', sql_contributions)

            self.load_tables('contributions')
        if options['expenditures']:
            self.construct_tables('expenditures', sql_expenditures)

            self.load_tables('expenditures')



    def construct_tables(self, table_name, query):
        drop_path = "IF object_id('dbo.new_%s') IS NOT NULL DROP TABLE new_%s" % (table_name, table_name)

        self.cursor.execute(drop_path)

        self.cursor.execute(query)

        self.cursor.commit()


    def load_tables(self, table_name):
        self.cursor.execute('DELETE FROM new_%s' % table_name)
        # path to data dir
        path = os.path.join(settings.BASE_DIR, 'data', '%s.csv') % table_name
        infile = open(path)

        csv_reader = csv.reader(infile, delimiter=',')
        csv_headers = csv_reader.next()
        for line in csv_reader:
            line = [l.replace("'", "''") for l in line]

            if table_name == 'contributions':
                headers = ','.join(contributions_header.values())
            elif table_name == 'expenditures':
                headers = ','.join(expenditures_header.values())
            else:
                pass

            insert_sql = '''
                INSERT INTO new_%s(%s)
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
            ''' % (table_name, headers, line[0].strip(), line[1].strip(), line[2].strip(), line[3].strip(), line[4].strip(), line[5].strip(), line[6].strip(), line[7].strip(), line[8].strip(), line[9].strip(), line[10].strip(), line[11].strip(), line[12].strip(), line[13].strip(), line[14].strip())

            self.cursor.execute(insert_sql)
            print csv_reader.line_num


        infile.close()
        self.cursor.commit()
