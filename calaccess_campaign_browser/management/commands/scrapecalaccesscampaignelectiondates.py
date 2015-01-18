import re
from datetime import datetime
from calaccess_campaign_browser.management.commands import ScrapeCommand
from calaccess_campaign_browser.models import Election
from .utils import parse_office_name


class Command(ScrapeCommand):
    help = "Scrape election dates from the Secretary of State's site"
    base_url = 'http://www.sos.ca.gov/elections/prior-elections\
/special-elections/'

    def build_results(self):
        results = {}

        self.header("Scraping election dates")

        # This is kind of heinous but first we need to
        # match up election descriptions to their raw ids.
        # That way we can disambiguate special elections in the same year.
        soup = self.make_request(
            'http://cal-access.ss.ca.gov/Campaign/\
Candidates/list.aspx?view=certified',
            abs=True
        )

        # Skip the first link, it is just "PRIOR ELECTIONS".
        election_id_map = {}
        links = soup.findAll('a', href=re.compile(r'^.*&electNav=\d+'))
        links = links[1:]
        for link in links:
            title = link.find_next_sibling('span').text.strip()
            election_id = re.match(r'.+electNav=(\d+)', link['href']).group(1)
            election_id_map[title] = int(election_id)

        # Now we can parse the actual dates.
        soup = self.make_request()
        # The first link is to a PDF that we don't need.
        links = soup.find('div', id='mainCont').find_all('a')
        links = links[1:]

        for link in links:
            office_name = link.text
            for li in link.find_next('ul').find_all('li'):
                match = re.match(r'(\w+) - (\w+ \d{1,2}, \d{4})', li.text)
                if match:
                    # Map the name from the election date site
                    # to the names used on the election ids site.
                    name = match.group(1).strip()
                    if name == 'General':
                        name = 'SPECIAL RUNOFF'
                    elif name == 'Primary':
                        name = 'SPECIAL ELECTION'
                    else:
                        name = 'OTHER'

                    date = match.group(2)
                    date = datetime.strptime(date, '%B %d, %Y').date()

                    # Figure out which id matches this election.
                    office, target_seat = parse_office_name(office_name)
                    if target_seat:
                        # Convert to int to avoid '4' != '04'.
                        target_seat = int(target_seat)
                    for election in election_id_map.keys():
                        data = re.match(r'(\d{4}).+(\d{2})', election)
                        if not data:
                            continue

                        # Again, cast to int to avoid annoying inconsistencies.
                        year = int(data.group(1))
                        seat = int(data.group(2))
                        if office in election and name in election and \
                                seat == target_seat and year == date.year:
                            id_raw = election_id_map[election]
                            results[id_raw] = date
                            if self.verbose:
                                self.log('Found election matching \
%s %s %s %s : %s' % (office, name target_seat, date.year, election))
                            break
                    else:
                        self.warn('Couldn\'t find an election \
matching %s' % office_name)
                        continue

        return results

    def process_results(self, results):
        for id_raw, date in results.items():
            try:
                election = Election.objects.get(id_raw=id_raw)

                if self.verbose:
                    self.log('Updating election %s' % election)
                election.date = date
                election.save()
            except Election.DoesNotExist:
                self.warn(
                    'Couldn\'t find an election matching id_raw=%s' % id_raw
                )
