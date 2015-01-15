import requests
from time import sleep
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from calaccess_campaign_browser.management.commands import CalAccessCommand


class ScrapeCommand(CalAccessCommand):
    base_url = 'http://cal-access.ss.ca.gov/'

    def handle(self, *args, **options):
        results = self.build_results()
        self.process_results(results)

    def url_for(self, rel_url):
        # Strip leading slash, if it exists.
        if rel_url[0] == '/':
            rel_url = rel_url[1:]
        return self.base_url + rel_url

    def make_request(self, rel_url, retries=1):
        url = self.url_for(rel_url)

        tries = 0
        while tries < retries:
            response = requests.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.text)
            else:
                tries += 1
                sleep(2.)
        raise HTTPError

    def build_results(self):
        raise NotImplementedError

    def process_results(self, results):
        raise NotImplementedError
