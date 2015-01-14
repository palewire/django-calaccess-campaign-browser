from django.core.management.base import BaseCommand, CommandError
#Scraper imports
from bs4 import BeautifulSoup
from time import sleep
import requests
from requests.exceptions import HTTPError
import re
import json

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
            for link in links:
                print link["href"]
                m = re.match(election_pattern, link['href'])
                if not m:
                    raise CommandError
                election_id = m.group(1)
                description = link.find_next_sibling('span').text.strip()
                print(election_id)
                print(description)
                try:
                    elections[description] = self.scrape_election_page(link["href"])

                # Try, try again
                except HTTPError:
                    print('Got non-200 response, trying again...')
                    sleep(2.)
                    elections[description] = self.scrape_election_page(link["href"])

                sleep(.5)

            print('Writing output to output.json....')
            with open('output.json', 'w') as out:
                json.dump(elections, out, sort_keys=True, indent=4, separators=(',', ': '))

    def scrape_election_page(self, rel_url):
        url = 'http://cal-access.ss.ca.gov'+rel_url
        print(url)
        response = requests.get(url)
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

            return sections

        else:
            raise HTTPError
