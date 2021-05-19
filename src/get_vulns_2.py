import pytest
import csv
from bs4 import BeautifulSoup
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from ..src.vulns import Vuln

class GetVulns:
    def __init__(self, package_name: str):
        self._package_name = package_name

    # Get the vulnerabilities and return the array
    def get_vulns(self):
        #Inizialize variables
        tmp_vulns_file = "../logs/tmp_vulns.csv"
        vulnerabilities = []
        tot_vulns = 0
        github_links = []
        # Loop among pages
        page = 0
        while(True):
            page += 1
            vulns_list_url = "https://snyk.io/vuln/page/" + str(page) + "?type=pip"
            try:
                req = Request(vulns_list_url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
            except (URLError, HTTPError, ConnectionResetError): break
            else:
                try:
                    # Get the list of vulnerabilities, if it exists
                    table = soup.findAll("tbody")[0]
                except Error: continue
                else:
                    for vuln_row in table.findAll("tr"):
                        try:
                            # For each vulnerability, try to gather its name, the severity, the URL,
                            # the related package name and the affected version from the row information
                            severity = vuln_row.findAll("span")[0].getText().strip()
                            name = vuln_row.findAll("strong")[0].getText().strip()
                            vuln_url = "https://snyk.io" + vuln_row.findAll("a")[0]["href"].strip()
                            if "/vuln/SNYK" not in vuln_url: vuln_url = ""
                            package_link = vuln_row.findAll("a")[1]
                            if "/vuln/pip:" not in package_link["href"]: package = ""
                            else: package = package_link.getText().strip()
                            versions = vuln_row.findAll("span", {"class": "semver"})[0].getText().strip()

                            if package == self._package_name:
                                tot_vulns += 1
                                # If the URL is not empty, retrieve all the reference URL related to the vulnerability
                                if vuln_url != "":
                                    vuln_info = Vuln(vuln_url).get_snyk_vuln_info()
                                    # If 'GitHub Commit' or 'GitHub PR' information has been found
                                    if vuln_info != "" and (vuln_info[2] != "" or vuln_info[6] != ""):
                                        commit_url = vuln_info[2]
                                        pr_url = vuln_info[6]
                                        if commit_url != "" and commit_url not in github_links:
                                            # Extract the hash out of the commit URL
                                            commit_hash = commit_url.split("/")[-1]
                                            hashtag_index = commit_hash.find("#")
                                            if hashtag_index != -1: commit_hash = commit_hash[:hashtag_index]
                                            question_index = commit_hash.find("?")
                                            if question_index != -1: commit_hash = commit_hash[:question_index]
                                            # If the commit hash is valid insert it into the list of vulnerabilities
                                            if commit_hash != "":
                                                github_links.append(commit_url)
                                                vulnerabilities.append([severity, commit_hash])
                                        elif pr_url != "" and pr_url not in github_links:
                                            # Extract the the commit URL
                                            if "commit" in pr_url: commit_url = pr_url
                                            elif "pull" in pr_url: 
                                                pr_url = pr_url.replace("/files", "")
                                                commit_url = Vuln(pr_url).get_commit_link_from_pr_link()
                                            else: commit_url = ""
                                            if commit_url != "":
                                                # Extract the hash out of the commit URL
                                                if "https://" not in commit_url: commit_url = "https://github.com" + commit_url
                                                commit_hash = commit_url.split("/")[-1]
                                                hashtag_index = commit_hash.find("#")
                                                if hashtag_index != -1: commit_hash = commit_hash[:hashtag_index]
                                                question_index = commit_hash.find("?")
                                                if question_index != -1: commit_hash = commit_hash[:question_index]
                                                # If the commit hash is valid insert it into the list of vulnerabilities
                                                if commit_hash != "":
                                                    github_links.append(commit_url)
                                                    vulnerabilities.append([severity, commit_hash])
                        except KeyError: continue

        # Print tmp file of vulnerabilities
        with open(tmp_vulns_file, mode='w') as vulns_csv_file:
            vulns_writer = csv.writer(vulns_csv_file, delimiter=';')
            vulns_writer.writerow(['Severity', 'Commit hash'])
            for vuln in vulnerabilities: vulns_writer.writerow(vulnerabilities[vuln])

        return [tot_vulns, len(vulnerabilities)]