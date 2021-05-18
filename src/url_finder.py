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
        self._pypi_url = URLFinder.real_pypi_url("https://pypi.org/project/{}".format(self._package_name))
        self._github_url = ""
        self._pypi_soup = None
        self._github_soup = None
        self.open_pypi_soup()

    @property
    def package_name(self) -> str:
        return self._package_name

    @property
    def github_url(self) -> str:
        return self._github_url

    @package_name.setter
    def package_name(self, package_name: str):
        self._package_name = package_name

    #@github_url.setter
    def set_github_url(self, github_url: str):
        self._github_url = URLFinder.real_github_url(github_url)
        self.open_github_soup()

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


    def mode_1(self) -> str:
        github_url_metadata = self.find_github_url_metadata()
        final_github_url = ""
        if github_url_metadata and self.test_url_working(self.normalize_url(github_url_metadata)):
            final_github_url = self.real_github_url(github_url_metadata)
        return final_github_url

    def mode_2(self) -> str:
        github_url_homepage = self.scrape_source_name_from_webpage(self.get_homepage())
        final_github_url = ""
        if github_url_homepage and self.test_url_working(self.normalize_url(github_url_homepage)):
            final_github_url = self.real_github_url(github_url_homepage)
        return final_github_url

    def mode_3(self) -> str:
        github_url_scraping = self.scrape_source_name_from_webpage(self._pypi_url)
        final_github_url = ""
        if github_url_scraping and self.test_url_working(self.normalize_url(github_url_scraping)):
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

    def find_github_url_from_pypi_page(self) -> str:
        """
        Get GitHub url from PyPi page
        """

        final_url = ""
        final_count = 0
        urls = {}
        #url = f"https://pypi.org/project/{self._package_name}"
        #try:
        #    req = Request(self._pypi_url, headers={'User-Agent': 'Mozilla/5.0'})
        #    soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        #except (ValueError, URLError, HTTPError, ConnectionResetError):
        #    return ""
        #else:
        if self._pypi_soup != None:
            # Examine all the links present in the PyPi page of that package
            for link in self._pypi_soup.findAll("a"):
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
                        if github_url[-1] == "/": github_url = github_url[:-1]
                        github_url_path_parts = url_parts.path.split("/")
                        github_url = "https://github.com/" + github_url_path_parts[1] + "/" + github_url_path_parts[2]
                        if "#" in github_url:
                            to_delete_index = github_url.index("#")
                            github_url = github_url[:to_delete_index]
                        if github_url in urls: urls[github_url] += 1
                        else: urls[github_url] = 1
                        #break

        for url in urls:
            count = urls[url]
            if count > final_count:
                final_count = count
                final_url = url

        # Return the normalized URL if working, otherwise return empty string
        if final_url != "" and self.test_url_working(self.normalize_url(final_url)): return self.real_github_url(final_url)
        else: return ""



    def find_ossgadget_url(self, type: str) -> str:
        """
        Find GitHub URL using OSSGadget tool, based on the type of source
        """
        # Launch the command and save the decoded result
        if type == "pypi": pkg = "pypi/" + self._package_name
        else: pkg = "github/" + self._package_name + "/" + self._package_name
        command = ["docker", "run", "ossgadget:latest", "/bin/bash", "-c", "./oss-find-source/bin/Debug/netcoreapp3.1/oss-find-source pkg:" + pkg]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE)
            decoded_result = result.stdout.decode('utf-8')
        except Exception: return ""
        else:
            if "No repositories were found after searching metadata." in decoded_result: github_url = ""
            # If a result has been found, take only the URL
            else: github_url = decoded_result.split(" ")[0][decoded_result.find("h"):]
            # Return the normalized URL if working, otherwise return empty string
            if github_url != "" and URLFinder.test_url_working(URLFinder.normalize_url(github_url)): 
                return URLFinder.real_github_url(github_url)
            else: 
                return ""

    def find_github_url_from_pypi_statistics(self) -> str:
        """
        Find GitHub URL from PyPI page statistics section
        """
        final_url = ""
        final_count = 0
        urls = {}
        if self._pypi_soup == None: return ""
        for div in self._pypi_soup.findAll("div", {"class": "github-repo-info"}):
            try:
                github_api_url = div["data-url"]
            except KeyError:
                # Link is not valid, go to the next line
                continue
            else:
                if github_api_url != "" and "github.com" in github_api_url and "github.com/sponsors/hynek" not in github_api_url:
                    if github_api_url[-1] == "/": github_api_url = github_api_url[:-1]
                    api_url_parts = urlparse(github_api_url)
                    if api_url_parts.path.count("/") == 3:
                        api_path_parts = api_url_parts.path.split("/")
                        stat_url = "https://github.com/" + api_path_parts[2] + "/" + api_path_parts[3]
                        stat_url = URLFinder.real_github_url(stat_url)
                        if stat_url != "":
                            if stat_url[-1] == "/": stat_url = stat_url[:-1]
                            if stat_url in urls: urls[stat_url] += 1
                            else: urls[stat_url] = 1

        for url in urls:
            count = urls[url]
            if count > final_count:
                final_count = count
                final_url = url

        return final_url

    def find_github_url_from_readthedocs(self) -> str:
        """
        Check if PyPI page have a "readthedocs.io" link, 
        search for a GitHub URL
        """
        final_url = ""
        final_count = 0
        link_url = ""
        link_count = 0
        urls = {}
        links = {}
        if self._pypi_soup == None: return ""
        for link1 in self._pypi_soup.findAll("a"):
            try:
                href_url = link1["href"].replace(" ", "")
                if "readthedocs.io" in href_url: 
                    if href_url in links: links[href_url] += 1
                    else: links[href_url] = 1
            except KeyError: continue

        for link in links:
            count = links[link]
            if count > link_count:
                link_count = count
                link_url = link

        if link_url != "":
            try:
                docs_req = Request(link_url, headers={'User-Agent': 'Mozilla/5.0'})
                docs_soup = BeautifulSoup(urlopen(docs_req).read(), features="html.parser")
            except (ValueError, URLError, HTTPError, ConnectionResetError): final_url = ""
            else:
                for link2 in docs_soup.findAll("a"):
                    try:
                        tmp_url = link2["href"]
                    except KeyError: continue
                    else:
                        tmp_url_parts = urlparse(tmp_url)
                        if self._package_name != "alabaster" and "bitprophet/alabaster" in tmp_url_parts.path: continue
                        elif self._package_name != "sphinx-rtd-theme" and "readthedocs/sphinx_rtd_theme" in tmp_url_parts.path: continue
                        if tmp_url_parts.netloc == "github.com" and tmp_url_parts.path.count("/") >= 2:
                            if tmp_url[-1] == "/": tmp_url = tmp_url[:-1]
                            tmp_url_path_parts = tmp_url_parts.path.split("/")
                            docs_github_url = "https://github.com/" + tmp_url_path_parts[1] + "/" + tmp_url_path_parts[2]
                            docs_github_url = URLFinder.real_github_url(docs_github_url)
                            if docs_github_url != "":
                                if docs_github_url[-1] == "/": docs_github_url = docs_github_url[:-1]
                                if docs_github_url in urls: urls[docs_github_url] += 1
                                else: urls[docs_github_url] = 1

        for url in urls:
            count = urls[url]
            if count > final_count:
                final_count = count
                final_url = url

        return final_url

    def find_github_url_from_pypi_badge(self) -> str:
        """
        Check if PyPI page have a GitHub badge linked to a GitHub URL
        """
        final_url = ""
        final_count = 0
        urls = {}
        if self._pypi_soup == None: return ""
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
                            if self._package_name != "black" and "psf/black" in badge_url_parts.path: continue
                            if badge_url_parts.path.count("/") >= 2:
                                badge_url_path_parts = badge_url_parts.path.split("/")
                                badge_url = "https://github.com/" + badge_url_path_parts[1] + "/" + badge_url_path_parts[2]
                                badge_url = URLFinder.real_github_url(badge_url)
                                if badge_url != "":
                                    if badge_url[-1] == "/": badge_url = badge_url[:-1]
                                    if badge_url in urls: urls[badge_url] += 1
                                    else: urls[badge_url] = 1

        for url in urls:
            count = urls[url]
            if count > final_count:
                final_count = count
                final_url = url

        return final_url



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

    #@staticmethod
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
        if url == "": return ""
        if url[0:2] == "//": url = url[2:]
        if url[-1] == "/": url = url[:-1]
        return "https://github.com" + urlparse(url).path.replace(".git", "").lower()

    @staticmethod
    def real_github_url(url: str) -> str:
        """
        Return the real GitHub URL, if it is a redirection
        """
        try:
            normalized_url = URLFinder.normalize_url(url)
            real_url_request = Request(normalized_url, headers={"User-Agent": "Mozilla/5.0"})
            real_url_response = urlopen(real_url_request)
            real_url = URLFinder.normalize_url(real_url_response.geturl())
            if real_url[-1] == "/": real_url = real_url[:-1]
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