import re
import urlparse
from time import sleep
from datetime import datetime
from calaccess_campaign_browser.management.commands import ScrapeCommand
from calaccess_campaign_browser.models import (
    Filer,
    Election,
    Proposition,
    PropositionFiler
)


class Command(ScrapeCommand):
    """
    Scrape propositions and ballot measures.
    """
    help = "Scrape links between filers and propositions from \
the CAL-ACCESS site"

    def build_results(self):
        self.header("Scraping propositions")

        # Build the link list from the 2013 page because otherwise the
        # other years are hidden under the "Historical" link.
        url = urlparse.urljoin(
            self.base_url,
            'Campaign/Measures/list.aspx?session=2013'
        )
        soup = self.get(url)

        # Filter links for uniqueness.
        links = soup.findAll('a', href=re.compile(r'^.*\?session=\d+'))
        links = list(set([link['href'] for link in links]))

        results = []
        for link in links:
            link = urlparse.urljoin(self.base_url, link)
            data = self.scrape_year_page(link)
            # Parse the year from the URL
            data['year'] = int(re.match(r'.+session=(\d+)', link).group(1))
            # Add it to the list
            results.append(data)
            sleep(0.5)

        # Pass it out
        return results

    def scrape_year_page(self, url):
        """
        Scrape data from a CAL-ACCESS page that publishes the list
        of propositions in a particular election year.
        """
        # Get the URL of the year page
        if self.verbosity > 2:
            self.log(' Scraping from %s' % url)
        soup = self.get(url)

        # Loop through all the tables on the page
        data_dict = {}
        table_list = soup.findAll(
            'table',
            {'id': re.compile(r'ListElections1__[a-z0-9]+')}
        )
        for table in table_list:

            # Pull the title
            election_title = table.select('caption span')[0].text

            # Log what we're up to
            if self.verbosity > 2:
                self.log('  Scraping %s' % election_title)

            # Pull the date
            election_date = re.match(
                r'[A-Z]+ \d{1,2}, \d{4}',
                election_title
            ).group(0)

            # Pull the type
            election_type = election_title.replace(election_date, '').strip()
            election_type = self.parse_election_name(election_type)

            # Get a list of the propositions in this table
            prop_links = table.findAll('a')

            # Scrape them one by one
            prop_list = [
                self.scrape_prop_page(
                    urlparse.urljoin(
                        self.base_url,
                        '/Campaign/Measures/%s' % link['href'],
                    )
                ) for link in prop_links
            ]

            # Add the data to our data dict
            data_dict[election_date] = {
                'type': election_type,
                'props': prop_list,
            }

        # Pass the data back out
        return data_dict

    def scrape_prop_page(self, url):
        """
        Scrape data from a proposition detail page
        """
        # Pull the page
        if self.verbosity > 2:
            self.log(' Scraping %s' % url)
        soup = self.get(url)

        # Create a data dictionary to put the good stuff in
        data_dict = {}

        # Add the title and id out of the page
        data_dict['name'] = soup.find('span', id='measureName').text
        data_dict['description'] = ''

        # If there is a " - " separating a name from a description
        # split it out below.
        if ' - ' in data_dict['name']:
            data_dict['name'], data_dict['description'] = data_dict['name'].split(" - ", 1)
            data_dict['name'] = data_dict['name'].strip()
            data_dict['description'] = data_dict['description'].strip()
        data_dict['id'] = re.match(r'.+id=(\d+)', url).group(1)

        data_dict['committees'] = []
        # Loop through all the tables on the page
        # which contain the committees on each side of the measure
        for table in soup.findAll('table', cellpadding='4'):

            # Pull the data box
            data = table.findAll('span', {'class': 'txt7'})

            # The URL
            url = table.find('a', {'class': 'sublink2'})

            # The name
            name = url.text

            # ID sometimes refers to xref_filer_id rather than filer_id_raw
            id_ = data[0].text

            # Does the committee support or oppose the measure?
            support = data[1].text.strip() == 'SUPPORT'

            # Put together a a data dictionary and add it to the list
            data_dict['committees'].append({
                'name': name,
                'id': id_,
                'support': support
            })

        # Pass the data out
        return data_dict

    def process_results(self, results):
        """
        Add the data to the database.
        """
        for d in results:
            for date, election_dict in d.items():

                # The years as extracted from the urls are actually not always
                # right, so get it from the date.
                if date == 'year':
                    continue
                date = datetime.strptime(date, '%B %d, %Y').date()
                try:
                    election = Election.objects.get(
                        year=date.year,
                        election_type=election_dict['type']
                    )
                    # Set the election date since we have it here
                    election.date = date
                    election.save()
                # Can't figure out to connect ambiguous elections, so None.
                except Election.MultipleObjectsReturned:
                    election = None
                    self.warn('  Multiple elections found')
                # If it doesn't exist, the same thing
                except Election.DoesNotExist:
                    election = None
                    self.warn('  Election does not exist')

                # Loop through the propositions
                for prop in election_dict['props']:

                    # Get or create it
                    prop_obj, c = Proposition.objects.get_or_create(
                        name=prop['name'],
                        description=prop['description'],
                        id_raw=prop['id']
                    )

                    # Log it
                    if self.verbosity > 2:
                        if c:
                            self.log('  Created %s' % prop_obj)

                    # Set the election if we have it
                    if election:
                        prop_obj.election = election
                        prop_obj.save()

                    # Now loop through the committees
                    for committee in prop['committees']:

                        # This filer_id could mean a lot of things, so try
                        filer_id = committee['id']
                        try:
                            filer = Filer.objects.get(filer_id_raw=filer_id)
                        except Filer.DoesNotExist:
                            try:
                                filer = Filer.objects.get(
                                    xref_filer_id=filer_id
                                )
                            except Filer.DoesNotExist:
                                self.warn(' Could not find existing filer')
                                continue

                        # Set the position
                        if committee['support']:
                            position = 'SUPPORT'
                        else:
                            position = 'OPPOSE'

                        # Associate the filer with the prop
                        pf, c = PropositionFiler.objects.get_or_create(
                            proposition=prop_obj,
                            filer=filer,
                            position=position
                        )

                        # Log it
                        if self.verbosity > 2:
                            self.log('   Linked %s' % pf)
