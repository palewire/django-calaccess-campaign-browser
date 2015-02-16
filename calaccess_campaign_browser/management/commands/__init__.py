import requests
from time import sleep
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from django.utils.termcolors import colorize
from django.core.management.base import BaseCommand


class CalAccessCommand(BaseCommand):

    def header(self, string):
        self.stdout.write(colorize(string, fg="cyan", opts=("bold",)))

    def log(self, string):
        self.stdout.write(colorize("%s" % string, fg="white"))

    def success(self, string):
        self.stdout.write(colorize(string, fg="green"))

    def failure(self, string):
        self.stdout.write(colorize(string, fg="red"))

    def warn(self, string):
        self.stdout.write(colorize(string, fg="yellow"))


class ScrapeCommand(CalAccessCommand):
    base_url = 'http://cal-access.ss.ca.gov/'

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])
        results = self.build_results()
        self.process_results(results)

    def build_results(self):
        """
        This method should perform the actual scraping
        and return the structured data.
        """
        raise NotImplementedError

    def process_results(self, results):
        """
        This method receives the structured data returned
        by `build_results` and should process it.
        """
        raise NotImplementedError

    def make_request(self, url, retries=1):
        """
        Convenience method for making a request
        to a url relative to the `base_url`,
        with built-in support for retries.
        Specify `abs=True` if passing an absolute url.
        """
        if self.verbosity > 2:
            self.log(" Retrieving %s" % url)
        tries = 0
        while tries < retries:
            response = requests.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.text)
            else:
                tries += 1
                sleep(2.0)
        raise HTTPError

    def parse_election_name(self, name):
        """
        Translates a raw election name into
        one of our canonical names.
        """
        name = name.upper()
        if 'PRIMARY' in name:
            return 'PRIMARY'
        elif 'GENERAL' in name:
            return 'GENERAL'
        elif 'SPECIAL RUNOFF' in name:
            return 'SPECIAL_RUNOFF'
        elif 'SPECIAL' in name:
            return 'SPECIAL'
        elif 'RECALL' in name:
            return 'RECALL'
        else:
            return 'OTHER'

    def parse_office_name(self, name):
        """
        Translates a raw office name into one of
        our canonical names and a seat (if available).
        """
        seat = None
        name = name.upper()
        if 'LIEUTENANT GOVERNOR' in name:
            office_type = 'LIEUTENANT_GOVERNOR'
        elif 'GOVERNOR' in name:
            office_type = 'GOVERNOR'
        elif 'SECRETARY OF STATE' in name:
            office_type = 'SECRETARY_OF_STATE'
        elif 'CONTROLLER' in name:
            office_type = 'CONTROLLER'
        elif 'TREASURER' in name:
            office_type = 'TREASURER'
        elif 'ATTORNEY GENERAL' in name:
            office_type = 'ATTORNEY_GENERAL'
        elif 'SUPERINTENDENT OF PUBLIC INSTRUCTION' in name:
            office_type = 'SUPERINTENDENT_OF_PUBLIC_INSTRUCTION'
        elif 'INSURANCE COMMISSIONER' in name:
            office_type = 'INSURANCE_COMMISSIONER'
        elif 'MEMBER BOARD OF EQUALIZATION' in name:
            office_type = 'BOARD_OF_EQUALIZATION'
            seat = name.split()[-1]
        elif 'SENATE' in name:
            office_type = 'SENATE'
            seat = name.split()[-1]
        elif 'ASSEMBLY' in name:
            office_type = 'ASSEMBLY'
            seat = name.split()[-1]
        else:
            office_type = 'OTHER'
        return office_type, seat