from optparse import make_option
from django.db import connection
from django.db.models import get_model
from django.db.utils import OperationalError
from django.core.management.base import LabelCommand
from calaccess_campaign_browser.management.commands import CalAccessCommand


def concat_stm(pref, idxs):
    parts = []
    if idxs[0] == 1:
        parts.append('%s_NAMT' % pref)
    if idxs[1] == 1:
        parts.append('%s_NAMF' % pref)
    if idxs[2] == 1:
        parts.append('%s_NAML' % pref)
    if idxs[3] == 1:
        parts.append('%s_NAMS' % pref)
    return 'concat(%s)' % ", ' ', ".join(parts)


def where_stm(pref, idxs):
    parts = []
    if idxs[0] == 1:
        parts.append("%s_NAMT != ''" % pref)
    else:
        parts.append("%s_NAMT = ''" % pref)
    if idxs[1] == 1:
        parts.append("%s_NAMF != ''" % pref)
    else:
        parts.append("%s_NAMF = ''" % pref)
    if idxs[2] == 1:
        parts.append("%s_NAML != ''" % pref)
    else:
        parts.append("%s_NAML = ''" % pref)
    if idxs[3] == 1:
        parts.append("%s_NAMS != ''" % pref)
    else:
        parts.append("%s_NAMS = ''" % pref)
    return ' and '.join(parts)


def despace(str):
    while str.find('  ') >= 0:
        str = str.replace('  ', ' ')
    return str


# TODO: generate a list of the digits of numbers
# from 1 to 15 in binary.
#
indexes_list = [
    [0,0,0,1],
    [0,0,1,0],
    [0,0,1,1],
    [0,1,0,0],
    [0,1,0,1],
    [0,1,1,0],
    [0,1,1,1],
    [1,0,0,0],
    [1,0,0,1],
    [1,0,1,0],
    [1,0,1,1],
    [1,1,0,0],
    [1,1,0,1],
    [1,1,1,0],
    [1,1,1,1]
]


class Command(CalAccessCommand):
    help = "Load CAL-ACCESS names"

    option_list = LabelCommand.option_list + (
        make_option(
            '--only-tables',
            dest="only_tables",
            help="Select only a limited set of tables to process."
        ),
        make_option(
            '--pre-delete',
            dest="pre_delete",
            help="Delete values from tables being processed before processing."
        ),
    )

    def handle(self, *args, **options):
        self.header("Loading names")

        only_tables = options['only_tables']
        pre_delete = options['pre_delete']

        # TODO: get this dict automatically by iterating through
        # the tables, finding columns that end in '_NAML' and getting
        # the prefixes from them.
        #
        prefixes = dict([
            ('CvrCampaignDisclosureCd', ['filer', 'tres', 'cand']),
            ('CvrE530Cd', ['filer', 'cand']),
            ('CvrLobbydisclosureCd', ['filer', 'sig', 'prn', 'major']),
            ('CvrRegistrationCd', ['filer', 'sig', 'prn']),
            ('CvrSoCd', ['filer', 'tres']),
            ('Cvr2CampaignDisclosureCd', ['enty', 'tres']),
            ('Cvr2LobbyDisclosureCd', ['enty']),
            ('Cvr2RegistrationCd', ['enty']),
            ('Cvr2SoCd', ['enty']),
            ('Cvr3VerificationInfoCd', ['sig']),
            ('DebtCd', ['payee', 'tres']),
            ('ExpnCd', ['payee', 'agent', 'tres', 'cand']),
            ('F501502Cd', ['cand', 'fin']),
            ('LattCd', ['recip']),
            ('LccmCd', ['recip', 'ctrib']),
            ('LempCd', ['cli']),
            ('LexpCd', ['payee']),
            ('LoanCd', ['lndr', 'tres', 'intr']),
            ('LobbyAmendmentsCd', ['a_l', 'd_l', 'a_le', 'd_le']),
            ('LothCd', ['subj']),
            ('LpayCd', ['emplr']),
            ('RcptCd', ['ctrib', 'tres', 'intr', 'cand']),
            ('S401Cd', ['agent', 'payee', 'cand']),
            ('S497Cd', ['enty', 'cand']),
            ('S498Cd', ['payor', 'cand'])])

        tables = prefixes.keys()

        if only_tables is not None:
            tables = list(set(tables).intersection(set(only_tables.split(','))))

        self.success('    tables: %s' % tables)

        tables_left = tables;

        for table in tables:

            target_table = str(get_model('calaccess_campaign_browser', 'Name')._meta.db_table)
            big_table = str(get_model('calaccess_raw', table)._meta.db_table)

            self.success('    table %s: %s' % (table, prefixes[table]))

            c = connection.cursor()

            if pre_delete:
                sql = "delete from %s where ext_table = '%s'" % (target_table, table)

                try:
                    c.execute(sql)
                except OperationalError:
                    self.failure('BAD SQL: %s' % sql)
                    self.failure('tables left: %s' % tables_left)
                    exit()

            for prefix in prefixes[table]:
                self.success('    current prefix: %s' % prefix)

                prefix = prefix.upper()

                for indexes in indexes_list:
                    sql = """
                        insert into %s
                        (ext_pk, ext_table, ext_prefix, namt, namf, naml, nams, name)
                        select id, '%s', '%s', %s_NAMT, %s_NAMF, %s_NAML, %s_NAMS,
                               %s
                        from %s
                        where %s
                        """ % (target_table,
                               table,
                               prefix.lower(),
                               prefix, prefix, prefix, prefix,
                               concat_stm(prefix,indexes),
                               big_table,
                               where_stm(prefix,indexes))
                        
                    sql = despace(sql).strip()

                    self.success('      %s' % indexes)
                    try:
                        c.execute(sql)
                    except OperationalError:
                        self.failure('BAD SQL: %s' % sql)
                        self.failure('tables left: %s' % tables_left)
                        exit()

            c.close()

            tables_left.remove(table)
