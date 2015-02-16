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
        soup = self.make_request(url)

        # Get all the links out
        links = soup.findAll('a', href=re.compile(r'^.*&electNav=\d+'))

        # Drop the link that says "prior elections" because it's a duplicate
        links = [
            l for l in links
                if l.find_next_sibling('span').text != 'Prior Elections'
        ]

        results = {}
        num_elections = len(links)
        for idx, link in enumerate(links):
            title = link.find_next_sibling('span').text.strip()

            results[title] = self.scrape_election_page(
                urlparse.urljoin(self.base_url, link["href"]),
                idx,
                num_elections
            )
            sleep(0.5)

        return results

    def process_results(self, results):
        self.log(' Creating and/or updating models...')
        self.log('  Found %s elections.' % len(results.keys()))
        for name, election_dict in results.items():

            self.log('  Processing %s' % name)
            election, created = Election.objects.get_or_create(
                year=int(name[:4]),
                name=self.parse_election_name(name),
                id_raw=election_dict['id'],
                sort_index=election_dict['index']
            )

            if self.verbosity > 2:
                if created:
                    self.log('  Created %s' % election)

            for _, office_dict in election_dict['data'].items():
                for office_name, candidates in office_dict.items():

                    office_type, seat = self.parse_office_name(office_name)
                    office, created = Office.objects.get_or_create(
                        name=office_type,
                        seat=seat
                    )

                    for candidate in candidates:
                        if not candidate['id']:
                            continue
                        try:
                            filer = Filer.objects.get(
                                filer_id_raw=int(candidate['id'])
                            )
                            candidate, c = Candidate.objects.get_or_create(
                                election=election,
                                office=office,
                                filer=filer
                            )
                        except Filer.DoesNotExist:
                            pass

    def scrape_election_page(self, url, idx, total_elections):
        sections = {}
        election_id = re.match(r'.+electNav=(\d+)', url).group(1)
        soup = self.make_request(url)

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

                if self.verbosity > 2:
                    self.log(' Scraping office %s' % title)

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

                sections[section_name][title] = people

        # The index value is used to preserve sorting of elections,
        # since multiple elections may occur in a year.
        # BeautifulSoup goes from top to bottom,
        # but the top most election is the most recent so it should
        # have the highest id.
        return {
            'id': int(election_id),
            'data': sections,
            'index': total_elections - idx
        }