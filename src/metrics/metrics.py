"""
This file contains methods to gather metrics of a GitHub repository
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


class Metrics:
    def __init__(self, package_name: str, github_url: str):
        self._package_name = package_name
        self._github_url = github_url
        self._closed_issues_url = ""

    @property
    def package_name(self) -> str:
        return self._package_name

    @property
    def github_url(self) -> str:
        return self._github_url

    @property
    def closed_issues_url(self) -> str:
        return self._closed_issues_url
    
    def get_link_metric_from_github_repo(self, metric:str) -> str:
        """
        Get a link metric of github repo
        """
        
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            for link in soup.findAll("a"):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    url_parts = urlparse(href_url)
                    if metric in url_parts.path:
                        output = link.getText().strip()
                        return self.convert_to_number(output)
            return ""

    def get_updated_at_from_github_repo(self) -> str:
        """
        Get updated_at of github repo
        """
        
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            try:
                div = soup.findAll("relative-time")[0]
                datetime = div["datetime"]
            except Error:
                return ""
            else:
                return datetime.strip()

    def get_commits_from_github_repo(self) -> str:
        """
        Get commits of github repo
        """
        
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            for link in soup.findAll("a"):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    url_parts = urlparse(href_url)
                    if "/commits/" in url_parts.path and "." not in href_url:
                        span = link.findAll("span")[0]
                        commits = span.findAll("strong")[0].getText().strip()
                        return self.convert_to_number(commits)
            return ""

    def get_commits2_from_github_repo(self) -> str:
        """
        Get commits of github repo
        """
        
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            for link in soup.findAll("a"):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    url_parts = urlparse(href_url)
                    if "/commits/" in url_parts.path:
                        span = link.findAll("span")[0]
                        commits = span.findAll("strong")[0].getText().strip()
                        return self.convert_to_number(commits)
            return ""

    def get_link_span_metric_from_github_repo(self, metric:str) -> str:
        """
        Get link span metric of github repo
        """
        
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            for link in soup.findAll("a"):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    url_parts = urlparse(href_url)
                    if metric in url_parts.path:
                        for span in link.findAll("span"):
                            try:
                                issues = span["title"]
                            except KeyError:
                                # Link is not valid, go to the next line
                                continue
                            else:
                                output = span.getText().strip()
                                return self.convert_to_number(output)
            return ""

    def get_tags_from_github_repo(self) -> str:
        """
        Get tags (releases) of github repo
        """
        
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            i = 0
            for link in soup.findAll("a", {"class": "link-gray-dark"}):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    url_parts = urlparse(href_url)
                    if "/releases" in url_parts.path:
                        i += 1
                        if i == 2:
                            tags = link.findAll("span", {"class": "text-bold"})[0].getText().strip()
                            return self.convert_to_number(tags)
            return ""


    def get_last_release_from_github_repo(self) -> str:
        """
        Get updated_at of github repo
        """
        
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            div = soup.findAll("relative-time")[1]
            try:
                datetime = div["datetime"]
            except KeyError:
                # Link is not valid, return
                return ""
            else:
                return datetime

    def get_dependent_url_from_github_repo(self) -> str:
        """
        Get dependent url of github repo
        """
        
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            for link in soup.findAll("a", {"class": "d-flex"}):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    url_parts = urlparse(href_url)
                    if "dependents" in url_parts.path:
                        return "https://github.com" + href_url.strip()
            return ""

    def get_closed_issues_from_github_repo(self) -> str:
        """
        Get issues url of github repo
        """
        
        try:
            req = Request(self._github_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            for link in soup.findAll("a"):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    url_parts = urlparse(href_url)
                    if "issues" in url_parts.path:
                        self._closed_issues_url = "https://github.com" + href_url.strip()
                        return self.get_closed_issues_from_closed_issues_url()
            return ""

    def get_dependent_from_github_repo(self, url: str, type: str) -> str:
        """
        Get dependent repositories or package of github repo
        """
        
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
           for link in soup.findAll("a"):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    if type in href_url:
                        return self.convert_to_number(link.getText().strip().split(' ', 1)[0])
           return ""

    def get_closed_issues_from_closed_issues_url(self) -> str:
        """
        Get closed issues of github repo
        """
        
        try:
            req = Request(self._closed_issues_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            return ""
        else:
            for link in soup.findAll("a"):
                try:
                    href_url = link["href"]
                except KeyError:
                    # Link is not valid, go to the next line
                    continue
                else:
                    if "issues?q=is%3Aissue+is%3Aclosed" in href_url:
                        return self.convert_to_number(link.getText().strip().split(' ', 1)[0])
            return ""

    @staticmethod
    def convert_to_number(n: str):
        """
        Convert a numeric string into a number
        """
        # Remove all not-numeric characters
        n = n.replace("+", "").replace(",", "").replace("?", "")
        # If the number is expressed in "k", remove it and multiply the number
        if "K" in n:
            if "." in n:
                dot_index = n.index(".")
                k_index = n.index("K")
                decimals = k_index - dot_index - 1
                if decimals == 1: return int(n.replace(".", "").replace("K", "")) * 100
                elif decimals == 2: return int(n.replace(".", "").replace("K", "")) * 10
            return int(n.replace("K", "")) * 1000
        if "k" in n:
            if "." in n:
                dot_index = n.index(".")
                k_index = n.index("k")
                decimals = k_index - dot_index - 1
                if decimals == 1: return int(n.replace(".", "").replace("k", "")) * 100
                elif decimals == 2: return int(n.replace(".", "").replace("k", "")) * 10
            return int(n.replace("k", "")) * 1000
        return int(n)