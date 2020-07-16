"""
This file contains description of a package in PyPI. This contains methods for obtaining the homepage,
codepage urls of the Package, collecting artifact urls of the Package.
"""
import logging
from urllib.request import Request, urlopen
import urllib
from urllib.error import URLError, HTTPError
import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, Iterator, List
from urllib.parse import urlparse
import validators
import os
import re
import requests
import collections


class Package:
    def __init__(self, package_name: str):
        self._package_name = package_name
        self._codepage = None
        self._homepage = None
        self._json_url = None 
        self._metadata_dict = None 

    @property
    def package_name(self) -> str:
        return self._package_name

    @package_name.setter
    def name(self, package_name: str) -> None:
        self._package_name = package_name

    @property
    def codepage(self) -> str:
        return self._codepage

    @codepage.setter
    def codepage(self, codepage: str) -> None:
        self._codepage = codepage

    @property
    def homepage(self) -> str:
        return self._homepage

    @homepage.setter
    def homepage(self, homepage: str) -> None:
        self._homepage = homepage

    @property
    def json_url(self) -> str:
        """
        Get the json url containing metadata of a package
        """
        if self._json_url is None:
            return f"https://pypi.org/pypi/{self._package_name}/json"
        else:
            return self._json_url

    @property
    def metadata_dict(self) -> Dict:
        if self.json_url is not None:
                with urlopen(self.json_url) as response:
                    return json.loads(response.read().decode())

    def extract_homepage(self) -> str:
        """
        Extract the homepage of a package. This will assign the homepage field of the package object.
        :return: a homepage url if it is found, otherwise None
        """
        if self.metadata_dict is not None:
            try:
                homepage =  self.metadata_dict["info"]["project_urls"]["Homepage"]
            except (TypeError, KeyError, HTTPError, URLError):
                return 
            else:
                return homepage[:-1] if homepage.endswith("/") else homepage

    def extract_codepage(self) -> str:
        """
        Extract the codepage of a package. This will assign the codepage field of the package object.
        :return: a codepage url if it is found, otherwise None
        """
        if self.metadata_dict is not None:
            try:
                codepage = next((value for key, value in self.metadata_dict["info"]["project_urls"].items() if 'code' in key.lower()), '')
            except AttributeError:
                return
            else:
                return codepage[:-1] if codepage.endswith("/") else codepage

    def extract_urls_from_metadata(self) -> List[str]:
        """
        Extract the codepage of a package. This will assign the codepage field of the package object.
        :return: a codepage url if it is found, otherwise None
        """
        if self.metadata_dict is not None:
            return re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(self.metadata_dict))

    @staticmethod
    def is_github_url(url: str) -> bool:
        """
        Determine if a url is a valid url in which it has a valid host and repository name
        :return: True - if url is valid otherwhise False
        """
        url_obj = urlparse(url)
        if "github.com" in url_obj.netloc: # checking url domain
            if url_obj.path.count("/") in [2, 3]: # checking if it has valid repository name
                return True
        return False

    def extract_github_url_from_webpage(self, url: str) -> str:
        """
        Scrape github urls from the homepage or codepage urls
        """
        regex = "[^a-zA-Z0-9]"
        github_urls_containing_package_name = []

        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return
        else:
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")

            for link in soup.findAll("a"):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    url_parts = urlparse(href_url)
                    if url_parts.netloc in ["github.com"]:
                        if self._package_name.replace(regex, "") in url_parts.path.replace(regex, ""):
                            github_urls_containing_package_name.append(href_url)

            # heuristics here: get only url that share common first parts
            scraped_url = os.path.commonprefix(github_urls_containing_package_name)
            if scraped_url:
                scraped_url = scraped_url[:-1] if scraped_url.endswith("/") else scraped_url
                return 'https://github.com' + "/".join(urlparse(scraped_url).path.split("/")[:3])

    def extract_homepage_codepage(self) -> str:
        """
        Extract source code repository url in homepage and codepage urls
        :return: a source code repository url if it is found, otherwise None
        """
        if self.is_github_url(self.extract_homepage()):
            return self.homepage

        if self.is_github_url(self.extract_codepage()):
            return self.codepage

    @staticmethod
    def is_url_working(url) -> bool:
        """
        Test if a url is working or not
        """
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return False
        else:
            if response.status_code == 200 and urlparse(url).path.count("/") == 2:
                return True
            else:
                return False

    def get_final_url(self) -> str:
        """
        Processing urls collecting from different sources to produce final url
        This is the function you want to use or extend, implements your logic here if you want to
        extract the github url in a new way
        """
        # Obtaining raw urls from various sources
        homepage = self.extract_homepage()
        codepage = self.extract_codepage()
        github_url = self.extract_homepage_codepage()
        scraped_url_homepage = self.extract_github_url_from_webpage(homepage)
        project_url = f"https://pypi.org/project/{self._package_name }"
        scraped_url_pypi = self.extract_github_url_from_webpage(project_url)

        # Checking the urls to find the final github url
        final_url = ""
        if github_url and self.is_url_working(github_url):
            final_url = github_url
        elif scraped_url_homepage and self.is_url_working(scraped_url_homepage):
            final_url = scraped_url_homepage
        elif scraped_url_pypi and self.is_url_working(scraped_url_pypi):
            final_url = scraped_url_pypi

        return final_url

