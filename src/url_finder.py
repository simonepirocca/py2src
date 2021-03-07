"""
This file contains description of a package in PyPI. This contains methods for
obtaining the homepage, codepage urls of the Package, collecting artifact urls
of the Package.
"""
import collections
import json
import logging
import os
import subprocess
from typing import Dict
from typing import Iterator
from typing import List
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen

import requests
import validators
from bs4 import BeautifulSoup

from .utils import log_function_output
from .constants import CONST

constants = CONST()

class URLFinder:
    """
    Package class represeting a PyPI package
    """

    def __init__(self, package_name: str):
        self._package_name = package_name
        self._pypi_url = URLFinder.real_pypi_url("https://pypi.org/project/{}".format(self._package_name))
        self._github_url = ""
        self._pypi_soup = None
        self._github_soup = None
        self.open_pypi_soup()

    @property
    def package_name(self) -> str:
        return self._package_name

    @package_name.setter
    def package_name(self, package_name: str):
        self._package_name = package_name

    def get_package_metadata_link(self) -> str:
        """Return the json metadata url of the package
        :return: the URL (str) of the package metadata
        """
        return constants.PYPI_PACKAGE_METADATA.format(self._package_name)

    def get_metadata(self) -> Dict:
        """ Get package metadata as json format
        :return: package metadata (dict)
        """
        package_json_url = self.get_package_metadata_link()
        with urlopen(package_json_url) as response:
            data = response.read().decode()
            package_medata = json.loads(data)
        return package_medata

    def get_package_url(self):
        """Get package url in PyPI"""
        return "https://pypi.org/project/{}".format(self._package_name)

    @staticmethod
    def is_valid_url(url: str, github_or_pypi: str) -> bool:
        """
        Determine if a url is a valid url in which it has a valid host and repository name
        :return: True - if url is valid otherwhise False
        """
        url_obj = urlparse(url)
        if github_or_pypi == "github":
            DOMAIN = constants.REPOSITORY_DOMAIN
        elif github_or_pypi == "pypi":
            DOMAIN = constants.PYPI_DOMAIN

        # checking url domain
        if DOMAIN in url_obj.netloc:  
            # checking if it has valid repository name by checking if it is the full url
            if url_obj.path.count("/") in [2, 3]: 
                return True
        return False

    @staticmethod
    def get_redirected_url(url: str) -> str:
        """
        Return the real GitHub URL, if it is a redirected url 
        :return: a redirected url string 
        """
        try:
            request = Request(url, headers=constants.REQUEST_HEADER)
            response = urlopen(request)
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return 
        else:
            redirected_url = response.geturl()
            return redirected_url 

    @staticmethod
    def is_url_working(url: str) -> bool:
        """
        Test if an url is working or not
        """
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return False
        else:
            if response.status_code == 200: 
                return True
            else:
                return False

    def find_url_from_homepage_metadata(self) -> str:
        """
        Extract the homepage of a package. This will assign the homepage field of the package object.
        :return: a homepage url if it is found, otherwise None
        """
        homepage_url = ""
        metadata_url = self.get_package_metadata_link()
        request = Request(metadata_url, headers=constants.REQUEST_HEADER)
        try:
            with urlopen(request) as response:
                data = json.loads(response.read().decode())
                homepage_metadata = data["info"]["project_urls"]["Homepage"]
        except (TypeError, KeyError, HTTPError, URLError):
            return
        else:
            if homepage_metadata.endswith("/"):
                homepage_url = homepage_metadata[:-1]
            else:
                homepage_url = homepage_metadata
        return homepage_url

    def find_github_url_from_homepage_metadata(self) -> str:
        """Validate if a url in homepage metadata is the working and a Github url
        :return: a valid Github and working URL
        """
        url_found = self.find_url_from_homepage_metadata()
        if self.validate_url(url_found, github_or_pypi="github"):
            return url_found

    def find_url_from_codepage_metadata(self) -> str:
        """
        Extract the codepage of a package. This will assign the codepage field of the package object.
        :return: a codepage url if it is found, otherwise None
        """
        metadata_url = self.get_package_metadata_link()
        url_request = Request(metadata_url, headers=constants.REQUEST_HEADER)
        codepage_url = ""
        try:
            with urlopen(url_request) as response:
                data = json.loads(response.read().decode())
        except (TypeError, HTTPError, URLError):
            return
        else:
            try:
                codepage_metadata = next(
                    (value
                    for key, value in data["info"]["project_urls"].items()
                    if "code" in key.lower()
                    ),"",
                    )
            except AttributeError:
                return
            else:
                if codepage_metadata.endswith("/"):
                    codepage_url = codepage_metadata[:-1]
                else:
                    codepage_url = codepage_metadata
        return codepage_url

    def validate_url(self, url, github_or_pypi: str) -> bool:
        """Validating an url (redirected url) is valid Github URL and working
        :return: valid and working Github url
        """
        if url is not None:
            url = self.get_redirected_url(url)
            url = self.normalize_url(url, github_or_pypi=github_or_pypi)
            if self.is_valid_url(url, github_or_pypi=github_or_pypi) and self.is_url_working(url):
                return True
            else:
                return False
        else:
            return False

    def find_github_url_from_codepage_metadata(self) -> str:
        """Validate if a url in codepage metadata is the working and a Github url
        :return: a valid Github and working URL
        """
        url_found = self.find_url_from_codepage_metadata()
        if self.validate_url(url_found, github_or_pypi="github"):
            return url_found

    @staticmethod
    def obtain_webpage_content(url: str):
        """Obtain the content of a webpage by requesting its url
        :return
        """
        try:
            req = Request(url, headers=constants.REQUEST_HEADER)
            response = urlopen(req)
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return
        else:
            return response.read()

    def find_all_urls_in_webpage(self, url: str) -> List[str]:
        """Find all URLs in a webpage
        :return: list of urls
        """
        webpage_content = self.obtain_webpage_content(url)
        soup = BeautifulSoup(webpage_content, features="html.parser")
        links = soup.findAll("a")
        all_urls = []
        for link in links:
            try:
                href_url = link["href"]
            except KeyError:
                # Link is not valid, go to the next line
                continue
            else:
                all_urls.append(href_url)
        
        return all_urls

    def find_all_github_urls_in_webpage(self, url: str) -> List[str]:
        """ Find all github urls in a webpage
        :return: a list of github urls in a webpage or empty list if there is no Github urls
        """
        logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG)
        all_urls = self.find_all_urls_in_webpage(url)
        github_urls = []
        for url_found in all_urls:
            url_parts = urlparse(url_found)
            if url_parts.netloc in [constants.REPOSITORY_DOMAIN]:
                github_urls.append(url_found)
        logger.info("All Github URLS: {}".format(github_urls))
        return github_urls

    @staticmethod
    def find_common_prefix_among_strs(list_strs: List) -> str:
        """ Find the common prefix of the items in the list
        :return: a common prefix str between strings
        """
        return os.path.commonprefix(list_strs)

    def find_github_urls_contain_package_name(self, url: str) -> List[str]:
        """Identify Github urls that contain the package name in their urls. This increases the 
        confidence that the Github urls are correct
        :return: list of Github urls that contain the package name
        """
        logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG)
        github_urls = self.find_all_github_urls_in_webpage(url)
        regex = "[^a-zA-Z0-9]"
        github_urls_contain_package_name = []
        for url_found in github_urls:
            url_parts = urlparse(url_found)
            if self._package_name.replace(regex, "") in url_parts.path.replace(regex, ""):
                github_urls_contain_package_name.append(url_found)
        logger.info("All Github URLS Containing package name: {}".format(github_urls_contain_package_name))
        return github_urls_contain_package_name

    def find_github_url_from_webpage(self, url: str) -> str:
        """Identify the common github url between all github urls found in a webpage
        This function requires all github urls sharing the same prefix Github url. 
        """
        all_github_urls = self.find_github_urls_contain_package_name(url)
        raw_url_found = self.find_common_prefix_among_strs(all_github_urls)
        if raw_url_found:
            if raw_url_found.endswith("/"):
                url_found = raw_url_found[:-1] 
            else:
                url_found = raw_url_found 
            #TODO: REFACTOR THIS LINE LATER AS IT IS COMPLICATED AND LONG
            return "https://{}".format(constants.REPOSITORY_DOMAIN) + "/".join(urlparse(url_found).path.split("/")[:3])

    def find_github_url_from_homepage_webpage(self) -> str:
        """Find the Github url in the homepage webpage
        :return: a URL (str) found in the homepage webpage
        """
        homepage_url_metadata = self.find_url_from_homepage_metadata()
        url_found = self.find_github_url_from_webpage(homepage_url_metadata)
        if self.validate_url(url_found, github_or_pypi="github"):
            return url_found

    def find_github_url_from_pypi_webpage(self) -> str:
        """Find the Github url in the PyPI webpage
        :return: a URL (str) found in the PyPI webpage
        """
        url_found = self.find_github_url_from_webpage(self.get_package_url())
        if self.validate_url(url_found, github_or_pypi="github"):
            return url_found

    def aggregate_github_urls(self) -> str:
        """
        Aggreate github urls collecting from various sources
        """
        # Obtaining raw urls from various sources
        github_url_homepage_metadata = self.find_github_url_from_homepage_metadata()
        github_url_codepage_metadata = self.find_github_url_from_codepage_metadata()
        homepage_url_metadata = self.find_url_from_codepage_metadata()
        github_url_homepage_webpage = self.find_github_url_from_webpage(github_url_)
        github_url_scraping = self.scrape_source_name_from_webpage(self.get_pypi_url())

        # Checking the urls to find the final github url
        final_github_url = ""
        if github_url_metadata and self.is_url_working(self.normalize_url(github_url_metadata)):
            final_github_url = self.real_github_url(github_url_metadata)
        elif github_url_homepage and self.is_url_working(self.normalize_url(github_url_homepage)):
            final_github_url = self.real_github_url(github_url_homepage)
        elif github_url_scraping and self.is_url_working(self.normalize_url(github_url_scraping)):
            final_github_url = self.real_github_url(github_url_scraping)

        return final_github_url

    def open_pypi_soup(self):
        """
        Open PyPI page setting the BeautifulSoup obj
        """
        try:
            req = Request(self._pypi_url, headers={'User-Agent': 'Mozilla/5.0'})
            self._pypi_soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            self._pypi_soup = None

    def open_github_soup(self):
        """
        Open GitHub page setting the BeautifulSoup obj
        """
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            self._github_soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            self._github_soup = None

    #def find_github_url_from_pypi_page(self) -> str:
    #    """
    #    Get GitHub url from PyPi page
    #    """

    #    github_url = ""
    #    if self._pypi_soup != None:
    #        # Examine all the links present in the PyPi page of that package
    #        for link in self._pypi_soup.findAll("a"):
    #            try:
    #                href_url = link["href"]
    #            except KeyError:
    #                # Link is not valid, go to the next line
    #                continue
    #            else:
    #                url_parts = urlparse(href_url)
    #                # Keep the first link that refers to a valid URL of GitHub project, that is not the "warehouse" project 
    #                if url_parts.netloc == "github.com" and url_parts.path.count("/") == 2 and "warehouse" not in url_parts.path:
    #                    github_url = href_url
    #                    break

    #    # Remove tag part from URL
    #    if "#" in github_url:
    #        to_delete_index = github_url.index("#")
    #        github_url = github_url[:to_delete_index]

    #    # Return the normalized URL if working, otherwise return empty string
    #    if github_url != "" and self.is_url_working(self.normalize_url(github_url)): 
    #        return self.real_github_url(github_url)
    #    else: 
    #        return ""

    def find_github_url_from_ossgadget(self) -> str:
        """
        Get GitHub url using OSSGadget tool
        """
        # Launch the OSSGadget command to see if it can found a URL linked to PyPi 
        github_url = self.launch_ossgadget_command("pypi/" + self._package_name)
        # Return the normalized URL if found...
        if(github_url != ""): return github_url
        else:
            #... Otherwise relaunch the command to see if it can found directly a GitHub URL 
            github_url = self.launch_ossgadget_command("github/" + self._package_name + "/" + self._package_name)
            if github_url != "": 
                return github_url
            else: 
                return ""

    @staticmethod
    def launch_ossgadget_command(pkg: str) -> str:
        """
        Launch OSSGadget tool to search the URL, based on the type of source
        """
        # Launch the command and save the decoded result
        command = ["docker", "run", "ossgadget:latest", "/bin/bash", "-c", "./oss-find-source/bin/Debug/netcoreapp3.1/oss-find-source pkg:" + pkg]
        result = subprocess.run(command, stdout=subprocess.PIPE)
        decoded_result = result.stdout.decode('utf-8')

        if "No repositories were found after searching metadata." in decoded_result: github_url = ""
        # If a result has been found, take only the URL
        else: github_url = decoded_result.split(" ")[0][decoded_result.find("h"):]
        # Return the normalized URL if working, otherwise return empty string
        if github_url != "" and URLFinder.is_url_working(URLFinder.normalize_url(github_url)): 
            return URLFinder.real_github_url(github_url)
        else: 
            return ""

    @staticmethod
    def normalize_url(url: str, github_or_pypi: str) -> str:
        """
        Normalize and construct the URL, taking just the lower version of the path, removing ".git" if needed
        :return: a normalized url string otherwise None
        """
        if url != "": 
            if url[0:2] == "//": 
                url = url[2:]
            if url[-1] == "/": 
                url = url[:-1]
            if github_or_pypi == "github":
                return constants.REPOSITY_FULL_DOMAIN + urlparse(url).path.replace(".git", "").lower()
            elif github_or_pypi == "pypi":
                return constants.PYPI_FULL_DOMAIN+ urlparse(url).path.replace(".git", "").lower()

    @staticmethod
    def real_github_url(url: str) -> str:
        """
        Return the real GitHub URL, if it is a redirection
        """
        try:
            normalized_url = URLFinder.normalize_url(url)
            real_url_request = Request(normalized_url, headers=constants.REQUEST_HEADER)
            real_url_response = urlopen(real_url_request)
            real_url = URLFinder.normalize_url(real_url_response.geturl())
            if real_url[-1] == "/": 
                real_url = real_url[:-1]
            return real_url
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""

    @staticmethod
    def normalize_pypi_url(url: str) -> str:
        """
        Normalize the URL, taking just the lower version of the path, removing ".git" if needed
        """
        if url == "": return ""
        if url[0:2] == "//": url = url[2:]
        if url[-1] == "/": url = url[:-1]
        return "https://pypi.org" + urlparse(url).path.replace(".git", "").lower()

    @staticmethod
    def real_pypi_url(url: str) -> str:
        """
        Return the real PyPI URL, if it is a redirection
        """
        try:
            real_url_request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            real_url_response = urlopen(real_url_request)
            real_url = real_url_response.geturl()
            if "pypi.org" in real_url: return URLFinder.normalize_pypi_url(real_url)
            else: return ""
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""

    def check_pypi_statistics(self) -> bool:
        """
        Check if PyPI page have statistics referring to GitHub URL.
        If it doesn't correspond, return the URL
        """
        other_link = ""
        if self._github_url == "" or self._pypi_soup == None: return False
        for div in self._pypi_soup.findAll("div", {"class": "github-repo-info"}):
            try:
                github_api_url = div["data-url"]
            except KeyError:
                # Link is not valid, go to the next line
                continue
            else:
                if github_api_url != "" and "github.com" in github_api_url:
                    if github_api_url[-1] == "/": github_api_url = github_api_url[:-1]
                    api_url_parts = urlparse(github_api_url)
                    if api_url_parts.path.count("/") == 3:
                        api_path_parts = api_url_parts.path.split("/")
                        stat_url = "https://github.com/" + api_path_parts[2] + "/" + api_path_parts[3]
                        stat_url = URLFinder.real_github_url(stat_url)
                        if stat_url != "":
                            if stat_url[-1] == "/": stat_url = stat_url[:-1]
                            if stat_url == self._github_url: return True
                            else: other_link = stat_url

        if other_link != "": return other_link
        return False

    def get_pypi_descr(self) -> str:
        """
        Get the project description on PyPI page
        """
        if self._pypi_soup == None: return ""
        for div in self._pypi_soup.findAll("div", {"class": "project-description"}):
            try:
                description = div.getText()
                if len(description) > 1500: description = description[:1500]
                return description
            except KeyError:
                # Link is not valid, go to the next line
                continue

        return ""

    def get_github_descr(self) -> str:
        """
        Get the project description on PyPI page
        """
        if self._github_soup == None: return ""
        for div in self._github_soup.findAll("div", {"class": "Box-body"}):
            try:
                description = div.getText()
                if len(description) > 1500: description = description[:1500]
                return description
            except KeyError:
                # Link is not valid, go to the next line
                continue

        return ""

    def check_readthedocs(self) -> bool:
        """
        Check if PyPI page have a "readthedocs.io" link, 
        and if it has a correspoding GitHub URL.
        If it doesn't correspond, return the URL
        """
        other_link = ""
        if self._github_url == "" or self._pypi_soup == None: return False
        for link1 in self._pypi_soup.findAll("a"):
            try:
                href_url = link1["href"].replace(" ", "")
                if "readthedocs.io" in href_url:
                    try:
                        docs_req = Request(href_url, headers={'User-Agent': 'Mozilla/5.0'})
                        docs_soup = BeautifulSoup(urlopen(docs_req).read(), features="html.parser")
                    except (ValueError, URLError, HTTPError, ConnectionResetError): continue
                    else:
                        for link2 in docs_soup.findAll("a"):
                            try:
                                tmp_url = link2["href"]
                            except KeyError: continue
                            else:
                                url_parts = urlparse(tmp_url)
                                if url_parts.netloc == "github.com" and url_parts.path.count("/") == 2 and "warehouse" not in url_parts.path:
                                    docs_github_url = URLFinder.real_github_url(tmp_url)
                                    if docs_github_url != "":
                                        if docs_github_url[-1] == "/": docs_github_url = docs_github_url[:-1]
                                        if docs_github_url == self._github_url: return True
                                        else: other_link = docs_github_url
            except KeyError: continue

        if other_link != "": return other_link
        return False

    def check_github_badge(self) -> bool:
        """
        Check if PyPI page have a GitHub badge referring to GitHub URL.
        If it doesn't correspond, return the URL
        """
        other_link = ""
        if self._github_url == "" or self._pypi_soup == None: return False
        for div in self._pypi_soup.findAll("div", {"class": "project-description"}):
            for badge in div.findAll("a"):
                if len(badge.findAll("img")) > 0:
                    try:
                        tmp_badge_url = badge["href"]
                    except KeyError: continue
                    else:
                        # It cares about both GitHub and Travis badges
                        if tmp_badge_url != "" and ("github.com" in tmp_badge_url or "travis-ci.org" in tmp_badge_url):
                            if tmp_badge_url[-1] == "/": tmp_badge_url = tmp_badge_url[:-1]
                            badge_url_parts = urlparse(tmp_badge_url)
                            if badge_url_parts.path.count("/") >= 2:
                                badge_url_path_parts = badge_url_parts.path.split("/")
                                badge_url = "https://github.com/" + badge_url_path_parts[1] + "/" + badge_url_path_parts[2]
                                badge_url = URLFinder.real_github_url(badge_url)
                                if badge_url != "":
                                    if badge_url[-1] == "/": badge_url = badge_url[:-1]
                                    if badge_url == self._github_url: return True
                                    else: other_link = badge_url

        if other_link != "": return other_link
        return False

    def check_pypi_badge(self) -> bool:
        """
        Check if GitHub page have a PyPI badge referring to PyPI URL
        """
        other_link = ""
        if self._pypi_url == "" or self._github_soup == None: return False
        for div in self._github_soup.findAll("div", {"class": "Box-body"}):
            for badge in div.findAll("a"):
                if len(badge.findAll("img")) > 0:
                    try:
                        tmp_badge_url = badge["href"].lower()
                        if tmp_badge_url != "":
                            if tmp_badge_url[-1] == "/": tmp_badge_url = tmp_badge_url[:-1]
                            badge_url = URLFinder.real_pypi_url(tmp_badge_url)
                            if badge_url != "" and "pypi.org" in badge_url:
                                if badge_url[-1] == "/": badge_url = badge_url[:-1]
                                badge_url = URLFinder.normalize_pypi_url(badge_url)
                                badge_url_parts = urlparse(badge_url)
                                if badge_url_parts.path.count("/") > 2:
                                    badge_url_path_parts = badge_url_parts.path.split("/")
                                    badge_url = "https://pypi.org/" + badge_url_path_parts[1] + "/" + badge_url_path_parts[2]
                                if badge_url == self._pypi_url: return True
                                else: other_link = badge_url
                    except KeyError: continue

        if other_link != "": return other_link
        return False

    def check_python_lang(self) -> str:
        """
        Check if GitHub page have Python as major language 
        """
        if self._pypi_url == "" or self._github_soup == None: return "0%"
        for div in self._github_soup.findAll("div", {"class": "BorderGrid-cell"}):
            languages_found = False
            for title in div.findAll("h2"):
                if title.getText() == "Languages":
                    languages_found = True
                    break
            if languages_found == True:
                for span in div.findAll("span"):
                    try:
                        language = span["aria-label"]
                        if "Python" in language and language.find(" ") != -1:
                            perc = language.split(" ")[1]
                            return perc + "%"
                    except KeyError: continue
        return "0%"

    def get_other_lang(self) -> str:
        """
        Get other languages in GitHub repo and relative percentage
        """
        other_lang = ""
        if self._pypi_url == "" or self._github_soup == None: return ""
        for div in self._github_soup.findAll("div", {"class": "BorderGrid-cell"}):
            languages_found = False
            for title in div.findAll("h2"):
                if title.getText() == "Languages":
                    languages_found = True
                    break
            if languages_found == True:
                for span in div.findAll("span"):
                    try:
                        language = span["aria-label"]
                        if "Python" not in language and language.find(" ") != -1:
                            lang_parts = language.split(" ")
                            lang = lang_parts[0]
                            perc = lang_parts[1]
                            other_lang += lang + " (" + perc + "%) - "
                    except KeyError: continue
        if other_lang != "": return other_lang[:-3]
        else: return ""
