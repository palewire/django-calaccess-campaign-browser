import csv
import os
import sys
import zipfile
from django.db import connection
from optparse import make_option
from calaccess_campaign_browser.management.commands import CalAccessCommand


custom_options = (
    make_option(
        '--only-years',
        dest="only_years",
        help="Select only a limited set, as comma-separated numbers, of the years' files to process."
    ),
    make_option(
        '--skip-years',
        dest="skip_years",
        help="Select only a limited set, as comma-separated numbers, of the years' files to process."
    ),
)


class Command(CalAccessCommand):
    help = "Merge Cal-Access IDs and DIME IDs."
    option_list = CalAccessCommand.option_list + custom_options

    def dotty(self, success):
        if success:
            sys.stdout.write('+')
        else:
            sys.stdout.write('.')
        sys.stdout.flush()

    def handle(self, *args, **options):
        """
        Merge DIME id values.
        """

        v = options['verbosity']

        if options['only_years'] is not None and options['skip_years'] is not None:
            print ''
            self.failure('Do not use both the --only-years and --skip-years parameters.')
            print ''
            exit()

        csvs = []

        filenames = next(os.walk('data/SSDS'))[2]

        for file in filenames:
            if file.endswith('.csv.zip'):
                csvs.append(file)

        if options['only_years'] is not None:
           self.success('    Only processing years: %s' % options['only_years'])
           only = []
           for year in options['only_years'].split(','):
               only.append('contribDB_%d.csv.zip' % int(year))
           all = set(csvs)
           csvs = list(all.intersection(set(only)))

        if options['skip_years'] is not None:
            self.success('    Processing all years except: %s' % options['skip_years'])
            for year in options['skip_years'].split(','):
                csvs.remove('contribDB_%d.csv.zip' % int(year))

        #self.success('    csv files:')
        #for csv_file in csvs:
        #    self.success('        %s' % csv_file)

        cnames = dict()
        rnames = dict()

        c = connection.cursor()

        # First get the names that we already have for both
        # recipients and contributors and make sure we do not
        # hit the database again for them.
        #
        sql = """
            select n1.name from calaccess_campaign_browser_identity n1,
                   calaccess_campaign_browser_identity_attribute a1
                   where n1.id = a1.identity_id and a1.att_name = 'bonica_cid'
        """

        c.execute(sql)

        for row in c:
            cnames[row[0].lower()] = 1

        sql = """
            select n1.name from calaccess_campaign_browser_identity n1,
                   calaccess_campaign_browser_identity_attribute a1
                   where n1.id = a1.identity_id and a1.att_name = 'bonica_rid'
        """

        c.execute(sql)

        for row in c:
            rnames[row[0].lower()] = 1

        self.success('    Already found names: rnames = %d, cnames = %d' % (len(rnames), len(cnames)))

        #self.success('    cnames:')
        #for name in cnames.keys():
        #    self.success('        "%s"' % name)
        #self.success('    rnames:')
        #for name in rnames.keys():
        #    self.success('        "%s"' % name)

        for csvName in csvs:

            csvFullName = 'data/SSDS/%s' % csvName
            print 'csvFullName: %s' % csvFullName

            zobj = zipfile.ZipFile(csvFullName, 'r')
            print 'zobj found: %s' % zobj

            zinfo = zobj.infolist()[0]
            print 'zipInfo found: "%s"' % zinfo

            zfile = zobj.open(zinfo)
            print 'zfile found: %s' % zfile

            rdr = csv.DictReader(zfile)
            print 'rdr found: %s' % rdr

            print ''

            while True:

                try:
                    row = rdr.next()
                except StopIteration:
                    break

                if row['contributor_name'] != '':

                    if row['contributor_name'].lower() not in cnames:

                        cnames[row['contributor_name'].lower()] = 1

                        sql = """
                            select id, name from calaccess_campaign_browser_identity
                            where name = '%s'
                        """ % row['contributor_name'].replace("'", "''")

                        c.execute(sql)

                        result = c.fetchone()

                        #print '    con result: %s' % result

                        if result is not None:

                            self.dotty(True)

                            #print ''
                            #print 'from "%s"' % row['contributor_name']
                            #print 'in cname: "%s"' % row['contributor_name'].lower()
                            #print result
                            #print ''

                            #self.success('    found cname: "%s"' % row['contributor_name'])
 
                            sql = """
                                insert into calaccess_campaign_browser_identity_attribute
                                (identity_id, att_name, att_value)
                                values (%d, 'bonica_cid', '%s')
                            """ % (int(result[0]), row['bonica_cid'])

                            try:
                                c.execute(sql)
                            except Exception, e:
                                print 'sql: "%s"' % sql
                                print 'exception: %s' % e
                                exit()

                        else:
                            self.dotty(False)

                    if row['recipient_name'].lower() not in rnames:

                        rnames[row['recipient_name'].lower()] = 1

                        sql = """
                            select id, name from calaccess_campaign_browser_identity
                            where name = '%s'
                        """ % row['recipient_name'].replace("'", "''")

                        c = connection.cursor()

                        c.execute(sql)

                        result = c.fetchone()

                        #print '    rec result: %s' % result

                        if result is not None:

                            self.dotty(True)

                            #print ''
                            #print 'from "%s"' % row['recipient_name']
                            #print 'in rname: "%s"' % row['recipient_name'].lower()
                            #print result
                            #print ''

                            #self.success('    found rname: "%s"' % row['recipient_name'])

                            sql = """
                                insert into calaccess_campaign_browser_identity_attribute
                                (identity_id, att_name, att_value)
                                values (%d, 'bonica_rid', '%s')
                            """ % (int(result[0]), row['bonica_rid'])

                            try:
                                c.execute(sql)
                            except Exception, e:
                                print 'sql: "%s"' % sql
                                print 'exception: %s' % e
                                exit()

                        else:
                            self.dotty(False)

                #print ''

            print ''

        c.close()
