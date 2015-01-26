# Python People Finder Scraper

Web scrapes a [people finder install](https://github.com/ministryofjustice/peoplefinder) and converts people in to python objects.

Requires a valid session token (can be obtained from the cookie data after logging in) and a base url.

## Example usage:

    from people_finder import PeopleFinder
    # Grab an instance of people finder
    pf = PeopleFinder(token, base_url)
    
    # Ask for a list page
    all_people = pf.get_people('teams/digital-services/people')
    >>> [Person, Person, Person, ...]
    all_people[0].name
    >>> "John Smith"
    all_people[0].url
    >>> "people/john-smith/"
    all_people[0].role
    >>> "Tester"

