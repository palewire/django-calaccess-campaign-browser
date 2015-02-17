import re
import urlparse
from time import sleep
from calaccess_campaign_browser.management.commands import ScrapeCommand
from calaccess_campaign_browser.models import (
    Election,
    Office,
    Candidate,
    Filer
)


class Command(ScrapeCommand):
    """
    Scraper to get the list of candidates per election.
    """
    help = "Scrape links between filers and elections from CAL-ACCESS site"

    def build_results(self):
        self.header("Scraping election candidates")

        url = urlparse.urljoin(
            self.base_url,
            '/Campaign/Candidates/list.aspx?view=certified&electNav=93'
        )
        soup = self.get(url)

        # Get all the links out
        links = soup.findAll('a', href=re.compile(r'^.*&electNav=\d+'))

        # Drop the link that says "prior elections" because it's a duplicate
        links = [
            l for l in links
            if l.find_next_sibling('span').text != 'Prior Elections'
        ]

        # Loop through the links...
        results = []
        for i, link in enumerate(links):
            # .. go and get each page and its data
            url = urlparse.urljoin(self.base_url, link["href"])
            data = self.scrape_page(url)
            # Parse out the name and year
            data['raw_name'] = link.find_next_sibling('span').text.strip()
            data['election_type'] = self.parse_election_name(data['raw_name'])
            data['year'] = int(data['raw_name'][:4])
            # The index value is used to preserve sorting of elections,
            # since multiple elections may occur in a year.
            # BeautifulSoup goes from top to bottom,
            # but the top most election is the most recent so it should
            # have the highest id.
            data['sort_index'] = len(links) - i
            # Add it to the list
            results.append(data)
            # Take a rest
            sleep(0.5)

        # Pass out the data
        return results

    def scrape_page(self, url):
        """
        Pull the elections and candidates from a CAL-ACCESS page.
        """
        # Go and get the page
        soup = self.get(url)

        # Loop through all the election sets on the page
        sections = {}
        for section in soup.findAll('a', {'name': re.compile(r'[a-z]+')}):

            # Check that this data matches the structure we expect.
            section_name_el = section.find('span', {'class': 'hdr14'})

            # If it doesn't just skip this one
            if not section_name_el:
                continue

            # Get the name out of page and key it in the data dictionary
            section_name = section_name_el.text
            sections[section_name] = {}

            # Loop thorugh all the rows in the section table
            for office in section.findAll('td'):

                # Check that this data matches the structure we expect.
                title_el = office.find('span', {'class': 'hdr13'})

                # If it doesn't, just quit no
                if not title_el:
                    continue

                # Log what we're up to
                if self.verbosity > 2:
                    self.log(' Scraping office %s' % title_el.text)

                # Pull the candidates out
                people = []
                for p in office.findAll('a', {'class': 'sublink2'}):
                    people.append({
                        'name': p.text,
                        'id': re.match(r'.+id=(\d+)', p['href']).group(1)
                    })

                for p in office.findAll('span', {'class': 'txt7'}):
                    people.append({
                        'name': p.text,
                        'id':  None
                    })

                # Add it to the data dictionary
                sections[section_name][title_el.text] = people

        return {
            'id': int(re.match(r'.+electNav=(\d+)', url).group(1)),
            'data': sections,
        }

    def process_results(self, results):
        self.log(' Creating and/or updating models...')
        self.log('  Found %s elections.' % len(results))

        # Loop through all the results
        for d in results:

            self.log('  Processing %s' % d['raw_name'])

            election, c = Election.objects.get_or_create(
                year=d['year'],
                election_type=d['election_type'],
                id_raw=d['id'],
                sort_index=d['sort_index']
            )

            if self.verbosity > 2:
                if c:
                    self.log('  Created %s' % election)

            # Loop through the data list from the scraped page
            for office_dict in d['data'].values():

                # Loop through each of the offices we found there
                for office_name, candidates in office_dict.items():

                    # Create an office object out of the data
                    office, c = Office.objects.get_or_create(
                        **self.parse_office_name(office_name)
                    )

                    # Log
                    if self.verbosity > 2:
                        if c:
                            self.log('  Created %s' % office)

                    # Loop through each of the candidates
                    for candidate in candidates:

                        # If it doesn't have an id, skip it.
                        if not candidate['id']:
                            continue
                        # If it does, try to find a matching Filer object
                        # and then add it to the database
                        try:
                            # Pull the Filer object from the database
                            filer = Filer.objects.get(
                                filer_id_raw=int(candidate['id'])
                            )

                            # Get or create the Candidate object
                            candidate, c = Candidate.objects.get_or_create(
                                election=election,
                                office=office,
                                filer=filer
                            )

                            # Log
                            if self.verbosity > 2:
                                if c:
                                    self.log('  Created %s' % candidate)

                        # And if there isn't filer just rock on
                        except Filer.DoesNotExist:
                            pass
