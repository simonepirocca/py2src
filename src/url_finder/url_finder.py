"""
This file contains description of a package in PyPI. This contains methods for obtaining the homepage,
codepage urls of the Package, collecting artifact urls of the Package.
"""
import collections
import json
import os
import subprocess
from typing import Dict
from typing import Iterator
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen

import requests
import validators
from bs4 import BeautifulSoup


class URLFinder:
    """
    Package class represeting a PyPI package
    """

    def __init__(self, package_name: str):
        self._package_name = package_name

    @property
    def package_name(self) -> str:
        return self._package_name

    @package_name.setter
    def package_name(self, package_name: str):
        self._package_name = package_name

    def get_json_url(self) -> str:
        """Return the json metadata url of the package"""
        return "https://pypi.org/pypi/{}/json".format(self._package_name)

    def get_metadata(self) -> Dict:
        package_json_url = self.get_json_url()
        with urlopen(package_json_url) as response:
            data = response.read().decode()
            package_medata = json.loads(data)
        return package_medata

    def get_artifact_time(self) -> Iterator[str]:
        """
        Get artifact publish time
        """
        metadata = self.get_metadata()
        for release in metadata["releases"].values():
            for archive in release:
                if archive["upload_time"]:
                    yield archive

    def get_artifact_urls(self) -> Iterator[str]:
        """
        Enumerate artifact urls of a package
        :return: an iterator of archive url string
        """
        metadata = self.get_metadata()
        for release in metadata["releases"].values():
            for archive in release:
                yield archive["url"]

    @staticmethod
    def is_valid_github_url(url: str) -> bool:
        """
        Determine if a url is a valid url in which it has a valid host and repository name
        :return: True - if url is valid otherwhise False
        """
        url_obj = urlparse(url)
        if "github.com" in url_obj.netloc:  # checking url domain
            if url_obj.path.count("/") in [
                2,
                3,
            ]:  # checking if it has valid repository name
                return True
        return False

    def scrape_source_name_from_webpage(self, url: str) -> str:
        """
        Scrape github urls from the homepage or codepage urls
        """
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            response = urlopen(req)
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return

        soup = BeautifulSoup(response.read(), features="html.parser")
        links = soup.findAll("a")

        urls = {}
        all_urls = []
        github_urls = []
        package_in_github_urls = []

        for link in links:
            try:
                href_url = link["href"]
            except KeyError:
                # Link is not valid, go to the next line
                continue
            else:
                validators.url(href_url)
                all_urls.append(href_url)
                url_parts = urlparse(href_url)
                if url_parts.netloc in ["github.com"]:
                    github_urls.append(href_url)
                    # if url_parts.path.count("/") in [2, 3]:
                    regex = "[^a-zA-Z0-9]"
                    if self._package_name.replace(regex, "") in url_parts.path.replace(
                        regex, ""
                    ):
                        package_in_github_urls.append(href_url)

        urls["all_urls"] = all_urls
        urls["github_urls"] = github_urls
        urls["package_in_github_urls"] = package_in_github_urls

        common_url = os.path.commonprefix(package_in_github_urls)
        if common_url:
            common_url = common_url[:-1] if common_url.endswith("/") else common_url
            common_url = "https://github.com" + "/".join(
                urlparse(common_url).path.split("/")[:3]
            )
            return common_url

    def find_github_url_metadata(self) -> str:
        """
        Extract source code repository url in homepage and codepage urls
        :return: a source code repository url if it is found, otherwise None
        """
        homepage_url = self.get_homepage()
        if homepage_url:
            if self.is_valid_github_url(homepage_url):
                return homepage_url

        codepage_url = self.get_codepage()
        if codepage_url:
            if self.is_valid_github_url(codepage_url):
                return codepage_url

    def get_homepage(self) -> str:
        """
        Extract the homepage of a package. This will assign the homepage field of the package object.
        :return: a homepage url if it is found, otherwise None
        """
        homepage_url = ""
        metadata_url = self.get_json_url()
        request = Request(metadata_url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urlopen(request) as response:
                data = json.loads(response.read().decode())
                homepage_metadata = data["info"]["project_urls"]["Homepage"]
        except (TypeError, KeyError, HTTPError, URLError):
            return
        else:
            homepage_url = (
                homepage_metadata[:-1]
                if homepage_metadata.endswith("/")
                else homepage_metadata
            )
        return homepage_url

    def get_codepage(self) -> str:
        """
        Extract the codepage of a package. This will assign the codepage field of the package object.
        :return: a codepage url if it is found, otherwise None
        """
        metadata_url = self.get_json_url()
        url_request = Request(metadata_url, headers={"User-Agent": "Mozilla/5.0"})
        codepage_url = ""
        try:
            with urlopen(url_request) as response:
                data = json.loads(response.read().decode())
        except (TypeError, HTTPError, URLError):
            return
        else:
            try:
                codepage_metadata = next(
                    (
                        value
                        for key, value in data["info"]["project_urls"].items()
                        if "code" in key.lower()
                    ),
                    "",
                )
            except AttributeError:
                return
            else:
                codepage_url = (
                    codepage_metadata[:-1]
                    if codepage_metadata.endswith("/")
                    else codepage_metadata
                )
        return codepage_url

    @staticmethod
    def test_url_working(url: str) -> bool:
        """
        Test if an url is working or not
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

    def get_pypi_url(self):
        """Get package url in PyPI"""
        return "https://pypi.org/project/{}".format(self._package_name)

    def find_github_url_from_metadata(self) -> str:
        """
        Aggreate github urls collecting from various sources
        """
        # Obtaining raw urls from various sources
        github_url_metadata = self.find_github_url_metadata()
        github_url_homepage = self.scrape_source_name_from_webpage(self.get_homepage())
        github_url_scraping = self.scrape_source_name_from_webpage(self.get_pypi_url())

        # Checking the urls to find the final github url
        final_github_url = ""
        if github_url_metadata and self.test_url_working(self.normalize_url(github_url_metadata)):
            final_github_url = self.real_github_url(github_url_metadata)
        elif github_url_homepage and self.test_url_working(self.normalize_url(github_url_homepage)):
            final_github_url = self.real_github_url(github_url_homepage)
        elif github_url_scraping and self.test_url_working(self.normalize_url(github_url_scraping)):
            final_github_url = self.real_github_url(github_url_scraping)

        return final_github_url

    def find_github_url_from_pypi_page(self) -> str:
        """
        Get GitHub url from PyPi page
        """

        github_url = ""
        url = f"https://pypi.org/project/{self._package_name}"
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            # Examine all the links present in the PyPi page of that package
            for link in soup.findAll("a"):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    url_parts = urlparse(href_url)
                    # Keep the first link that refers to a valid URL of GitHub project, that is not the "warehouse" project 
                    if url_parts.netloc == "github.com" and url_parts.path.count("/") == 2 and "warehouse" not in url_parts.path:
                        github_url = href_url
                        break

        # Remove tag part from URL
        if "#" in github_url:
            to_delete_index = github_url.index("#")
            github_url = github_url[:to_delete_index]

        # Return the normalized URL if working, otherwise return empty string
        if github_url != "" and self.test_url_working(self.normalize_url(github_url)): return self.real_github_url(github_url)
        else: return ""

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
            if(github_url != ""): return github_url
            else: return ""

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
        if github_url != "" and URLFinder.test_url_working(URLFinder.normalize_url(github_url)): return URLFinder.real_github_url(github_url)
        else: return ""

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize the URL, taking just the lower version of the path, removing ".git" if needed
        """
        if url[0:2] == "//": url = url[2:]
        return "https://github.com" + urlparse(url).path.replace(".git", "").lower()

    @staticmethod
    def real_github_url(url: str) -> str:
        """
        Return the real GitHub URL, if it is a redirection
        """
        real_url_request = Request(URLFinder.normalize_url(url), headers={"User-Agent": "Mozilla/5.0"})
        real_url_response = urlopen(real_url_request)
        real_url = URLFinder.normalize_url(real_url_response.geturl())
        return real_url