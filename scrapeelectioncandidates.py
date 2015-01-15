from django.core.management.base import BaseCommand, CommandError
#Scraper imports
from bs4 import BeautifulSoup
from time import sleep
import requests
from requests.exceptions import HTTPError
import re
from calaccess_campaign_browser.models import Election, Office, Candidate, Filer

class Command(BaseCommand):

    def handle(self, *args, **options):
        help = 'scraper to get the list of candidates per election'
        election_pattern = re.compile('^.*electNav=(\d+)')
        url =  \
            'http://cal-access.ss.ca.gov/Campaign/Candidates/list.aspx?view=certified'

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text)
            links = soup.findAll('a', href = re.compile(r'^.*&electNav=\d+'))
            elections = {}

            # Skip the first link, it is just "PRIOR ELECTIONS".
            print('Scraping...')
            links = links[1:]
            num_elections = len(links)
            for idx, link in enumerate(links):
                m = re.match(election_pattern, link['href'])
                if not m:
                    raise CommandError

                election_id = m.group(1)
                description = link.find_next_sibling('span').text.strip()

                try:
                    elections[description] = self.scrape_election_page(link["href"], idx, num_elections)

                # Try, try again
                except HTTPError:
                    print('Got non-200 response, trying again...')
                    sleep(2.)
                    elections[description] = self.scrape_election_page(link["href"], idx, num_elections)

                sleep(.5)

            print('Creating and/or updating models...')
            print('Found %s elections.' % len(elections.keys()))
            for name, election_dict in elections.items():
                print('Election: %s' % name)
                election_id = election_dict['id']

                year = int(name[:4])

                if 'PRIMARY' in name:
                    type = 'PRIMARY'
                elif 'GENERAL' in name:
                    type = 'GENERAL'
                elif 'SPECIAL RUNOFF' in name:
                    type = 'SPECIAL_RUNOFF'
                elif 'SPECIAL' in name:
                    type = 'SPECIAL'
                elif 'RECALL' in name:
                    type = 'RECALL'
                else:
                    type = 'OTHER'

                election, created = Election.objects.get_or_create(
                        year=year,
                        name=type,
                        id_raw=election_id,
                        sort_index=election_dict['index'])

                if created:
                    print('\tCreated %s' % election)
                else:
                    print('\tGot %s' % election)

                for _, office_dict in election_dict['data'].items():
                    for office_name, candidates in office_dict.items():
                        seat = None
                        if 'LIEUTENANT GOVERNOR' in office_name:
                            office_type = 'LIEUTENANT_GOVERNOR'
                        elif 'GOVERNOR' in office_name:
                            office_type = 'GOVERNOR'
                        elif 'SECRETARY OF STATE' in office_name:
                            office_type = 'SECRETARY_OF_STATE'
                        elif 'CONTROLLER' in office_name:
                            office_type = 'CONTROLLER'
                        elif 'TREASURER' in office_name:
                            office_type = 'TREASURER'
                        elif 'ATTORNEY GENERAL' in office_name:
                            office_type = 'ATTORNEY_GENERAL'
                        elif 'SUPERINTENDENT OF PUBLIC INSTRUCTION' in office_name:
                            office_type = 'SUPERINTENDENT_OF_PUBLIC_INSTRUCTION'
                        elif 'INSURANCE COMMISSIONER' in office_name:
                            office_type = 'INSURANCE_COMMISSIONER'
                        elif 'MEMBER BOARD OF EQUALIZATION' in office_name:
                            office_type = 'BOARD_OF_EQUALIZATION'
                            seat = office_name.split()[-1]
                        elif 'STATE SENATE' in office_name:
                            office_type = 'SENATE'
                            seat = office_name.split()[-1]
                        elif 'ASSEMBLY' in office_name:
                            office_type = 'ASSEMBLY'
                            seat = office_name.split()[-1]
                        else:
                            office_type = 'OTHER'

                        office, created = Office.objects.get_or_create(name=office_type, seat=seat)

                        for candidate in candidates:
                            if not candidate['id']:
                                continue

                            try:
                                filer = Filer.objects.get(filer_id_raw=int(candidate['id']))
                                candidate, created = Candidate.objects.get_or_create(election=election, office=office, filer=filer)
                            except Filer.DoesNotExist:
                                pass



    def scrape_election_page(self, rel_url, idx, total_elections):
        url = 'http://cal-access.ss.ca.gov'+rel_url
        print('Scraping from %s' % url)
        response = requests.get(url)
        election_id = url.replace('http://cal-access.ss.ca.gov/Campaign/Candidates/list.aspx?view=certified&electNav=', '')
        if response.status_code == 200:
            soup = BeautifulSoup(response.text)
            sections = {}
            for section in soup.findAll('a', {'name': re.compile(r'[a-z]+')}):
                # Check that this data matches the structure we expect.
                section_name_el = section.find('span', {'class': 'hdr14'})
                if not section_name_el:
                    continue
                section_name = section_name_el.text
                sections[section_name] = {}

                offices = section.findAll('td')
                for office in offices:
                    # Check that this data matches the structure we expect.
                    title_el = office.find('span', {'class': 'hdr13'})
                    if not title_el:
                        continue
                    title = title_el.text

                    people = []
                    for p in office.findAll('a', {'class': 'sublink2'}):
                        people.append({
                            'name': p.text,
                            'id':  p['href'].replace('/Campaign/Candidates/Detail.aspx?id=', '')
                        })
                    for p in office.findAll('span', {'class': 'txt7'}):
                        people.append({
                            'name': p.text,
                            'id':  None
                        })

                    sections[section_name][title] = people

            # The index value is used to preserve sorting of elections,
            # since multiple elections may occur in a year.
            # BeautifulSoup goes from top to bottom,
            # but the top most election is the most recent so it should have the highest id.
            return {
                'id': int(election_id),
                'data': sections,
                'index': total_elections - idx
            }

        else:
            raise HTTPError
