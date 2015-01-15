import re
from time import sleep
from calaccess_campaign_browser.management.commands import ScrapeCommand
from calaccess_campaign_browser.models import Election, Office, Candidate, Filer
from .utils import parse_election_name, parse_office_name


class Command(ScrapeCommand):
    """
    Scraper to get the list of candidates per election.
    """
    def build_results(self):
        results = {}
        soup = self.make_request('Campaign/Candidates/list.aspx?view=certified')

        # Skip the first link, it is just "PRIOR ELECTIONS".
        links = soup.findAll('a', href=re.compile(r'^.*&electNav=\d+'))
        links = links[1:]

        self.header("Scraping election candidates")
        num_elections = len(links)
        for idx, link in enumerate(links):
            title = link.find_next_sibling('span').text.strip()
            results[title] = self.scrape_election_page(
                link["href"],
                idx,
                num_elections)
            sleep(.5)

        return results

    def process_results(self, results):
        self.header('Creating and/or updating models...')
        self.log('Found %s elections.' % len(results.keys()))
        for name, election_dict in results.items():
            self.log('Election: %s' % name)
            election_id = election_dict['id']

            year = int(name[:4])
            type = parse_election_name(name)

            election, created = Election.objects.get_or_create(
                year=year,
                name=type,
                id_raw=election_id,
                sort_index=election_dict['index'])

            if created:
                self.log('\tCreated %s' % election)
            else:
                self.log('\tGot %s' % election)

            for _, office_dict in election_dict['data'].items():
                for office_name, candidates in office_dict.items():
                    office_type, seat = parse_office_name(office_name)

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
        self.header('Scraping from %s' % rel_url)

        sections = {}
        election_id = re.match(r'.+electNav=(\d+)', rel_url).group(1)
        soup = self.make_request(rel_url)
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

                self.log('\tScraping office %s' % title)
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
