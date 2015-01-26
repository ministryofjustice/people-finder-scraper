import re
import json
import sys

import requests
from bs4 import BeautifulSoup


class PeopleFinderScraperMixIn(object):
    """
    Shared methods for scraping people finder.
    """
    def __init__(self, session_token, base_url, session_key=None):
        if not session_key:
            session_key = '_moj_peoplefinder_session'
        self.session_token = session_token
        self.cookie_data = {
            'seen_cookie_message': 'yes',
            session_key: self.session_token,
        }

        self.base_url = base_url
        self.session = requests.Session()

    def make_url(self, url):
        return "%s%s" % (self.base_url, url)

    def get_page(self, url):
        if not url.startswith('http'):
            url = self.make_url(url)
        return self.session.get(url, cookies=self.cookie_data, verify=False)


class Person(PeopleFinderScraperMixIn):
    """
    A Person is a representation of a person URL on people finder.

    Given a URL, attributes are lazily loaded from the remote URL.
    Optionally a person can be created from a list page.
    """
    def __init__(self, session_token, base_url):
        super(Person, self).__init__(session_token, base_url)
        self.cache = {}

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "%s (%s)" % (
            self.name.encode('utf8'),
            self.url.encode('utf8'),
            )

    def _lazy_get(self, key):
        if self.cache.get(key):
            return self.cache[key]
        # Get a soup object, as we're going to need it
        if not hasattr(self, 'soup'):
            self.soup = BeautifulSoup(self.get_page(self.url).text)

    @property
    def name(self):
        key = 'name'
        cache = self._lazy_get(key)
        if cache:
            return cache

        self.cache[key] = self.soup.find('h1').text
        return self.cache[key]

    @property
    def email(self):
        key = 'email'
        cache = self._lazy_get(key)
        if cache:
            return cache

        self.cache[key] = self.soup.find('main').find('a', {
            'href': re.compile('^mailto')}).text
        return self.cache[key]

    @property
    def role(self):
        key = 'role'
        cache = self._lazy_get(key)
        if cache:
            return cache

        self.cache[key] = self.soup.find('main').find('dd', {
            'class': 'breadcrumbs'}).previous().text
        return self.cache[key]

    @property
    def teams(self):
        key = 'teams'
        cache = self._lazy_get(key)
        if cache:
            return cache

        teams_list = []
        for team in self.soup.find('main').find('dd', {
            'class': 'breadcrumbs'}).findAll('li'):
            teams_list.append({
                'name': team.text.strip(),
                'url': team.find('a')['href'],
            })

        self.cache[key] = teams_list
        return teams_list

    @classmethod
    def from_list_page(cls, soup, session_token, base_url):
        """
        Provides parsing for the person HTML on the list pages.

        Get's everything possible and sets the URL.  Everything else can
        be lazy loaded.
        """
        person = cls(session_token, base_url)
        person.cache['name'] = soup.find('h4').text
        person.url = soup.find('a')['href']
        person.image_url = soup.find('img')['src']
        person.cache['role'] = soup.find('div', {'class': 'role'}).text
        return person

    def as_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'email': self.email,
            'role': self.role,
            'teams': self.teams,
        }


class PeopleFinder(PeopleFinderScraperMixIn):
    """
    Handles interactions with people finder's team page.
    """
    def get_people(self, base_url):
        page = self.get_page(base_url)
        soup = BeautifulSoup(page.text)
        people = soup.findAll('div', {'class': 'team-member'})
        return [
            Person.from_list_page(
                person, session_token=self.session_token,
                base_url=self.base_url
            ) for person in people]

    def ds_people(self):
        ds_people_url = self.make_url("teams/digital-services/people")
        return self.get_people(ds_people_url)

    def ds_devs(self):
        ds_people_url = self.make_url("teams/development")
        return self.get_people(ds_people_url)


if __name__ == "__main__":
    if not len(sys.argv) >= 3:
        raise ValueError('Please provide your session token and base url')
    token = sys.argv[1]
    base_url = sys.argv[2]
    pf = PeopleFinder(token, base_url)
    devs = pf.ds_devs()

    print json.dumps([dev.as_dict() for dev in devs], indent=4)
