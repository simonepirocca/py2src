"""
This file contains methods to gather information about a SNYK vulnerability,
starting from a SNYK or GitHub URL
"""
from urllib.request import Request, urlopen
import urllib
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup

class Vuln:
    def __init__(self, vuln_url: str):
        self._vuln_url = vuln_url
        self._soup = None
        try:
            req = Request(vuln_url, headers={'User-Agent': 'Mozilla/5.0'})
            self._soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            self._soup = ""

    @property
    def vuln_url(self) -> str:
        return self._vuln_url

    @property
    def soup(self) -> BeautifulSoup:
        return self._soup

    def get_snyk_vuln_info(self):
        """
        Get a list of information regarding a snyk vulnerability
        """
        cve = self.find_cve()
        github_advisory = self.find_ref_url("GitHub Advisory")
        github_commit = self.find_ref_url("GitHub Commit")
        github_release = self.find_ref_url("GitHub Release")
        github_release_tag = self.find_ref_url("GitHub Release Tag")
        github_add_inf = self.find_ref_url("GitHub Additional Information")
        github_pr = self.find_ref_url("GitHub PR")
        github_issue = self.find_ref_url("GitHub Issue")
        nvd = self.find_ref_url("NVD")

        vuln_info = [cve, github_advisory, github_commit, github_release,\
 github_release_tag, github_add_inf, github_pr, github_issue, nvd]
        return vuln_info

    def find_cve(self) -> str:
        """
        Get CVE information crawling vulnerability's page
        """
        if self._soup != "":
            for a in self._soup.findAll("a"):
                cve = a.getText().strip()
                if "CVE-" in cve: return cve
            return ""
        return ""

    def find_ref_url(self, name: str) -> str:
        """
        Get a reference URL of a vulnerability crawling its page
        """
        if self._soup != "":
            for a in self._soup.findAll("a"):
                if name == a.getText().strip(): return a["href"].strip()
            return ""
        return ""

    def get_commit_link_from_pr_link(self) -> str:
        """
        Get the commit link crwling a PR link page
        """
        if self._soup != "":
            for div in self._soup.findAll("div", {"class", "TimelineItem-body"}):
                # merged case
                div_text = div.getText()
                if "merged commit" in div_text:
                    for link in div.findAll("a"):
                        try:
                            href_url = link["href"]
                        except KeyError:
                            # Link is not valid, go to the next line
                            continue
                        else:
                            if "/commit/" in href_url: return href_url

                # closed case
                elif "closed this" in div_text:
                    for code in div.findAll("code"):
                        for link in code.findAll("a"):
                            try:
                                href_url = link["href"]
                            except KeyError:
                                # Link is not valid, go to the next line
                                continue
                            else:
                                if "/commit/" in href_url: return href_url

            # open case or not found
            return ""
        return ""