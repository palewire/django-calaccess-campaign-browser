from django.db import connection
from django.core.management.base import BaseCommand
from calaccess_campaign_browser.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.load_candidates()

    def load_candidates(self):
        """
        Load all of the distinct candidate filers into the Filing table.
        """
        print "- Loading candidates into consolidated Filer model"
        c = connection.cursor()
        c.execute('DELETE FROM %s' % Filer._meta.db_table)
        sql = """
        INSERT INTO %s (
            filer_id,
            status,
            effective_date,
            xref_filer_id,
            filer_type,
            name
        )
        SELECT
         FILERNAME_CD.`FILER_ID` as filer_id,
         FILERNAME_CD.`STATUS` as status,
         FILERNAME_CD.`EFFECT_DT` as effective_date,
         FILERNAME_CD.`XREF_FILER_ID` as xref_filer_id,
        -- Marking these as candidate record in our target data table
         'cand' as filer_type,
        -- Combining and cleaning up the name data from the source
         REPLACE(TRIM(CONCAT(`NAMT`, " ", `NAMF`, " ", `NAML`, " ", `NAMS`)), '  ', ' ') as name
        FROM FILERNAME_CD
        INNER JOIN (
            -- Joining against a subquery that returns the last record
            -- in the source table because there are duplicates and we
            -- do not know of any logical way to better infer the most 
            -- recent or complete record.
            SELECT FILER_ID, MAX(`id`) as `id`
            FROM FILERNAME_CD
            -- This filter limits the source data to only candidate filers
            WHERE `FILER_TYPE` = 'CANDIDATE/OFFICEHOLDER'
            GROUP BY 1
        ) as max
        ON FILERNAME_CD.`id` = max.`id`
        """ % (
            Filer._meta.db_table,
        )
        c.execute(sql)

#    def oldschool(self, *args, **kwargs):
#        """
#        Take a look in the Filings table and just
#        load up the filers that have filed a 460 or a 450.
#        Load the candidates first,
#        linking them to all the committees they control.
#        Then load the rest of the committees.
#        """
#        candidate_cmte_list = []
#        # all filers of type candidate
#        all_candidate_filer_ids = (
#            FilernameCd
#            .objects
#            .filter(filer_type='CANDIDATE/OFFICEHOLDER')
#            .values_list('filer_id', flat=True)
#            .distinct()
#        )

#        for filer_id in all_candidate_filer_ids:
#            # querying by filer_id_a gets list of
#            # connected recipient committees
#            qs_linked = (
#                FilerLinksCd
#                .objects
#                .filter(Q(filer_id_a=filer_id) | Q(filer_id_b=filer_id))
#                .filter(link_type='12011')
#            )

#            filer_a_ids = list(
#                (
#                    qs_linked
#                    .values_list('filer_id_a', flat=True)
#                    .exclude(filer_id_a=filer_id)
#                )
#            )

#            filer_b_ids = list(
#                (
#                    qs_linked
#                    .values_list('filer_id_b', flat=True)
#                    .exclude(filer_id_b=filer_id)
#                )
#            )

#            cmte_filer_ids = filer_a_ids + filer_b_ids

#            if len(cmte_filer_ids) > 0:  # has a linked committee
#                # build a list of all candidate committees so can exclude for
#                # pac import
#                candidate_cmte_list.extend(cmte_filer_ids)
#                # query to see if there are any filings associated with the
#                # committee
#                qs_cmte_filings = FilerFilingsCd.objects.filter(
#                    filer_id__in=cmte_filer_ids)
#                # has data associated with a committee
#                if qs_cmte_filings.count() > 0:
#                    candidate_filer_name_obj = (
#                        FilernameCd
#                        .objects
#                        .filter(filer_id=filer_id)
#                        .order_by('-effect_dt')
#                        .exclude(naml='')[0]
#                    )

#                    candidate_filer_obj, created = Filer.objects.get_or_create(
#                        filer_id=filer_id,
#                        status=candidate_filer_name_obj.status,
#                        filer_type='cand',
#                        effective_date=candidate_filer_name_obj.effect_dt,
#                        xref_filer_id=candidate_filer_name_obj.xref_filer_id,
#                        name=(
#                            '{0} {1} {2} {3}'
#                            .format(
#                                candidate_filer_name_obj.namt,
#                                candidate_filer_name_obj.namf,
#                                candidate_filer_name_obj.naml,
#                                candidate_filer_name_obj.nams
#                            )
#                            .strip()
#                        )
#                    )

#                    if created:
#                        for cmte_filer_id in cmte_filer_ids:
#                            qs_this_cmte_filings = (
#                                qs_cmte_filings
#                                .filter(filer_id=cmte_filer_id)
#                                .values_list('filing_id', flat=True)
#                            )

#                            # filings have data
#                            summary_count = (
#                                SmryCd
#                                .objects
#                                .filter(
#                                    filing_id__in=(
#                                        list(qs_this_cmte_filings)
#                                    )
#                                )
#                                .count()
#                            )

#                            if summary_count > 0:
#                                candidate_filer_obj.active = True
#                                candidate_filer_obj.save()

#                                qs_names = (
#                                    FilernameCd
#                                    .objects
#                                    .filter(filer_id=cmte_filer_id)
#                                    .order_by('-effect_dt')
#                                    .exclude(naml='')
#                                )

#                                if qs_names.count() > 0:
#                                    cmte_filer_name_obj = qs_names[0]

#                                    cmte_obj, cmte_created = (
#                                        Committee
#                                        .objects
#                                        .get_or_create(
#                                            filer=candidate_filer_obj,
#                                            filer_id_raw=cmte_filer_id,
#                                            name=(
#                                                '{0} {1} {2} {3}'
#                                                .format(
#                                                    cmte_filer_name_obj.namt,
#                                                    cmte_filer_name_obj.namf,
#                                                    cmte_filer_name_obj.naml,
#                                                    cmte_filer_name_obj.nams
#                                                )
#                                                .strip()
#                                            ),
#                                            committee_type='cand',
#                                        )
#                                    )

#        print 'candidates and their linked committees loaded'

#        all_filings = (
#            FilerFilingsCd
#            .objects
#            .filter(Q(form_id='F460') | Q(form_id='F450'))
#            .values_list('filing_id', flat=True)
#            .distinct()
#        )

#        all_filings_with_data = (
#            SmryCd
#            .objects
#            .filter(filing_id__in=all_filings)
#            .values_list('filing_id', flat=True)
#            .distinct()
#        )

#        # if you swap filing_id for filer_id in the values clause you
#        # get the same count of filings as in all_filings_with_data
#        all_filers_with_data = (
#            FilerFilingsCd
#            .objects
#            .filter(filing_id__in=all_filings_with_data)
#            .exclude(filer_id__in=candidate_cmte_list)
#            .values_list('filer_id', flat=True)
#            .distinct()
#        )

#        for pac_filer_id in all_filers_with_data:
#            pac_filer_name = FilernameCd.objects.filter(filer_id=pac_filer_id)

#            if pac_filer_name.count() > 0:
#                pac_filer_name_obj = pac_filer_name.order_by(
#                    '-effect_dt').exclude(naml='')[0]

#                pac_filer_obj, created = Filer.objects.get_or_create(
#                    filer_id=pac_filer_id,
#                    status=pac_filer_name_obj.status,
#                    filer_type='pac',
#                    effective_date=pac_filer_name_obj.effect_dt,
#                    xref_filer_id=pac_filer_name_obj.xref_filer_id,
#                    name=(
#                        '{0} {1} {2} {3}'
#                        .format(
#                            pac_filer_name_obj.namt,
#                            pac_filer_name_obj.namf,
#                            pac_filer_name_obj.naml,
#                            pac_filer_name_obj.nams
#                        )
#                        .strip()
#                    ),
#                )
#                qs_pac_filings = FilerFilingsCd.objects.filter(
#                    filer_id=pac_filer_id)

#                if qs_pac_filings.count() > 0:
#                    qs_pac_smry = (
#                        SmryCd
#                        .objects
#                        .filter(
#                            filing_id__in=(
#                                list(
#                                    qs_pac_filings
#                                    .values_list('filing_id', flat=True)
#                                )
#                            )
#                        )
#                    )

#                    if qs_pac_smry.count() > 0:
#                        pac_filer_obj.active = True
#                        pac_filer_obj.save()

#                pac_cmte_obj, pac_created = Committee.objects.get_or_create(
#                    filer=pac_filer_obj,
#                    filer_id_raw=pac_filer_id,
#                    name=(
#                        '{0} {1} {2} {3}'
#                        .format(
#                            pac_filer_name_obj.namt,
#                            pac_filer_name_obj.namf,
#                            pac_filer_name_obj.naml,
#                            pac_filer_name_obj.nams
#                        )
#                        .strip()
#                    ),
#                    committee_type = 'pac',
#                )

#        print 'loaded non-candidate linked committees with associated filings'
#    # Need to fix duped committee issue and deal with controlling filer thing.
