from django.core.management.base import BaseCommand, CommandError
#Scraper imports
from bs4 import BeautifulSoup
from time import sleep
import requests
import re

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
            for link in links:
                print link["href"]
                m = re.match(election_pattern, link['href'])
                if not m:
                    raise CommandError
                election_id = m.group(1)
                description = link.find_next_sibling('span').text.strip()
                print election_id
                print description
                self.scrapeElectionPage(link["href"])
                sleep(.5)

    def scrapeElectionPage(self, rel_url):
        url = 'http://cal-access.ss.ca.gov'+rel_url
        print url
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text)
            titles = soup.findAll('span', { "class" : "hdr13" })
            print len(titles)
            
