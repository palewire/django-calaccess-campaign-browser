from django.core.management.base import BaseCommand, CommandError

# Scraper imports
import re
from time import sleep
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from calaccess_campaign_browser.models import Filer, Election, Proposition, PropositionFiler


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Scrape propositions and ballot measures.
        """
        prop_pattern = re.compile('^.*session=(\d+)')

        # Build the link list from this page because otherwise the other years
        # are hidden under the "Historical" link.
        url =  \
            'http://cal-access.ss.ca.gov/Campaign/Measures/list.aspx?session=2013'

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text)
            links = soup.findAll('a', href=re.compile(r'^.*\?session=\d+'))
            years = {}

            # Filter links for uniqueness.
            links = list(set([link['href'] for link in links]))

            print('Scraping...')
            for link in links:
                m = re.match(prop_pattern, link)
                if not m:
                    raise CommandError

                year = link.replace('/Campaign/Measures/list.aspx?session=', '')

                try:
                    years[year] = self.scrape_props_page(link)

                # Try, try again
                except HTTPError:
                    print('Got non-200 response, trying again...')
                    sleep(2.)
                    years[year] = self.scrape_props_page(link)

                sleep(.5)

            for year, elections in years.items():
                # The years as extracted from the urls are actually not always
                # right, so get it from the date.
                for date, election_dict in elections.items():
                    date = datetime.strptime(date, '%B %d, %Y').date()

                    # Skip future elections?
                    if date.year > datetime.now().year:
                        continue

                    try:
                        election = Election.objects.get(year=date.year, name=election_dict['type'])
                        election.date = date
                        election.save()

                    # Can't figure out to connect ambiguous elections, just set to None.
                    except Election.MultipleObjectsReturned:
                        election = None
                        print('Multiple elections found for year %s and type %s, not sure which to pick. \
                                Not setting the date for this election...' % (date.year, election_dict['type']))

                    for prop in election_dict['props']:
                        proposition, created = Proposition.objects.get_or_create(name=prop['name'], filer_id_raw=prop['id'])

                        if created:
                            print('\tCreated %s' % proposition)
                        else:
                            print('\tGot %s' % proposition)

                        proposition.election = election
                        proposition.save()

                        for committee in prop['committees']:
                            print('\t\tCommittee %s' % committee['id'])

                            # This filer_id could mean a lot of things, so try a few.
                            filer_id = committee['id']
                            try:
                                filer = Filer.objects.get(filer_id_raw=filer_id)
                            except Filer.DoesNotExist:
                                try:
                                    filer = Filer.objects.get(xref_filer_id=filer_id)
                                except Filer.DoesNotExist:
                                    print('\t\t\tCould not find existing filer for id %s' % filer_id)
                                    pass

                            # Associate the filer with the prop.
                            PropositionFiler.objects.get_or_create(
                                proposition=proposition,
                                filer=filer,
                                position='SUPPORT' if committee['support'] else 'OPPOSE'
                            )

    def scrape_props_page(self, rel_url):
        url = 'http://cal-access.ss.ca.gov'+rel_url
        print('Scraping from %s' % url)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text)
            elections = {}
            for election in soup.findAll('table', {'id': re.compile(r'ListElections1__[a-z0-9]+')}):
                election_title = election.select('caption span')[0].text
                election_date = re.match(r'[A-Z]+ \d{1,2}, \d{4}', election_title).group(0)
                election_type = election_title.replace(election_date, '').strip()
                prop_links = election.findAll('a')

                print('\tScraping election %s...' % election_title)

                # Translate to our election types.
                if 'PRIMARY' in election_type:
                    election_type = 'PRIMARY'
                elif 'GENERAL' in election_type:
                    election_type = 'GENERAL'
                elif 'SPECIAL RUNOFF' in election_type:
                    election_type = 'SPECIAL_RUNOFF'
                elif 'SPECIAL' in election_type:
                    election_type = 'SPECIAL'
                elif 'RECALL' in election_type:
                    election_type = 'RECALL'
                else:
                    election_type = 'OTHER'

                elections[election_date] = {
                    'type': election_type,
                    'props': [self.scrape_prop_page(link['href']) for link in prop_links]
                }
            return elections
        else:
            raise HTTPError

    def scrape_prop_page(self, rel_url):
        url = 'http://cal-access.ss.ca.gov/Campaign/Measures/' + rel_url
        print('\tScraping from %s' % url)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text)
            prop_name = soup.find('span', id='measureName').text
            print(rel_url)
            prop_id = re.match(r'.+id=(\d+)', rel_url).group(1)
            committees = []

            print('\t\tScraping measure %s' % prop_name)

            # Targeting elements by cellpadding is hacky but...
            for committee in soup.findAll('table', cellpadding='4'):
                data = committee.findAll('span', {'class': 'txt7'})

                url = committee.find('a', {'class': 'sublink2'})
                name = url.text

                # This ID sometimes refers to xref_filer_id rather than filer_id_raw.
                id = data[0].text
                # This is one matches with filer_id_raw, always.
                # id = re.match(r'.+id=(\d+)', url).group(1)

                support = data[1].text.strip() == 'SUPPORT'
                committees.append({
                    'name': name,
                    'id': id,
                    'support': support
                })

                print('\t\t\t%s (%s) [%s]' % (name, id, support))

            return {
                'id': prop_id,
                'name': prop_name,
                'committees': committees
            }

        else:
            raise HTTPError
