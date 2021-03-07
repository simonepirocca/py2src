from .url_finder import URLFinder
from .utils import get_soup_obj
from .constants import CONST

constants = CONST()

class PyPIMetric(URLFinder):
    def __init__(self, package_name: str):
        URLFinder.__init__(self, package_name)

    def get_bs_soup(self):
        """Get beautifulsoup object from the PyPI webpage content 

        """
        pypi_package_url = self.get_package_url()
        soup = get_soup_obj(pypi_package_url)
        return soup

    def find_github_badge(self) -> str:
        """Finding a Github badge in PyPI webpage. It checks two repo
        identifiers: GitHub and Travis badges
        """
        soup = self.get_bs_soup()
        for div in soup.findAll("div", {"class": "project-description"}):
            for badge in div.findAll("a"):
                # Github or travis badges usually found in img tags
                if len(badge.findAll("img")) > 0:
                    try:
                        url_found = badge["href"]
                    except KeyError: 
                        continue
                    else:
                        if url_found != "":
                            #print(url_found)
                            if (constants.REPOSITORY_DOMAIN in url_found) or (constants.TRAVIS_DOMAIN in url_found):
                                if self.validate_url(url_found, github_or_pypi="github"):
                                    return url_found 

