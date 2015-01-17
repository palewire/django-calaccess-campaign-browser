import re
from time import sleep
from datetime import datetime
from calaccess_campaign_browser.management.commands import ScrapeCommand
from calaccess_campaign_browser.models import Filer, Election, Proposition, PropositionFiler
from .utils import parse_election_name


class Command(ScrapeCommand):
    """
    Scrape propositions and ballot measures.
    """
    help = "Scrape links between filers and propositions from \
the CAL-ACCESS site"

    def build_results(self):
        results = {}

        # Build the link list from the 2013 page because otherwise the
        # other years are hidden under the "Historical" link.
        soup = self.make_request('Campaign/Measures/list.aspx?session=2013')

        # Filter links for uniqueness.
        links = soup.findAll('a', href=re.compile(r'^.*\?session=\d+'))
        links = list(set([link['href'] for link in links]))

        self.header("Scraping propositions")
        for link in links:
            year = re.match(r'.+session=(\d+)', link).group(1)
            results[year] = self.scrape_props_page(link)
            sleep(.5)

        return results

    def process_results(self, results):
        for year, elections in results.items():
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
                    self.warn('Multiple elections found for year %s and type %s, not sure which to pick. \
                    Not setting the date for this election...' % (date.year, election_dict['type']))

                for prop in election_dict['props']:
                    proposition, created = Proposition.objects.get_or_create(name=prop['name'], filer_id_raw=prop['id'])

                    if self.verbose:
                        if created:
                            self.log('\tCreated %s' % proposition)
                        else:
                            self.log('\tGot %s' % proposition)

                    proposition.election = election
                    proposition.save()

                    for committee in prop['committees']:
                        if self.verbose:
                            self.log('\t\tCommittee %s' % committee['id'])

                        # This filer_id could mean a lot of things, so try a few.
                        filer_id = committee['id']
                        try:
                            filer = Filer.objects.get(filer_id_raw=filer_id)
                        except Filer.DoesNotExist:
                            try:
                                filer = Filer.objects.get(xref_filer_id=filer_id)
                            except Filer.DoesNotExist:
                                self.warn('\t\t\tCould not find existing filer for id %s' % filer_id)
                                pass

                        # Associate the filer with the prop.
                        PropositionFiler.objects.get_or_create(
                            proposition=proposition,
                            filer=filer,
                            position='SUPPORT' if committee['support'] else 'OPPOSE'
                        )

    def scrape_props_page(self, rel_url):
        if self.verbose:
            self.header('Scraping from %s' % rel_url)
        else:
            self.log('Scraping from %s' % rel_url)
        soup = self.make_request(rel_url)
        elections = {}
        for election in soup.findAll('table', {'id': re.compile(r'ListElections1__[a-z0-9]+')}):
            election_title = election.select('caption span')[0].text
            election_date = re.match(r'[A-Z]+ \d{1,2}, \d{4}', election_title).group(0)
            election_type = election_title.replace(election_date, '').strip()
            prop_links = election.findAll('a')

            if self.verbose:
                self.log('\tScraping election %s...' % election_title)

            election_type = parse_election_name(election_type)

            elections[election_date] = {
                'type': election_type,
                'props': [self.scrape_prop_page(link['href']) for link in prop_links]
            }
        return elections

    def scrape_prop_page(self, rel_url):
        rel_url = '/Campaign/Measures/' + rel_url

        if self.verbose:
            self.header('\tScraping from %s' % rel_url)

        soup = self.make_request(rel_url)
        prop_name = soup.find('span', id='measureName').text
        prop_id = re.match(r'.+id=(\d+)', rel_url).group(1)
        committees = []

        if self.verbose:
            self.log('\t\tScraping measure %s' % prop_name)

        # Targeting elements by cellpadding is hacky but...
        for committee in soup.findAll('table', cellpadding='4'):
            data = committee.findAll('span', {'class': 'txt7'})

            url = committee.find('a', {'class': 'sublink2'})
            name = url.text
            # This ID sometimes refers to xref_filer_id rather than filer_id_raw.
            id = data[0].text
            support = data[1].text.strip() == 'SUPPORT'
            committees.append({
                'name': name,
                'id': id,
                'support': support
            })

            if self.verbose:
                self.log('\t\t\t%s (%s) [%s]' % (name, id, support))

        return {
            'id': prop_id,
            'name': prop_name,
            'committees': committees
        }
