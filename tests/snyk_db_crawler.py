"""
This file get all the missing github url related to package names
"""
import sys
import os
import csv
from bs4 import BeautifulSoup
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
sys.path.append(os.path.abspath("../src/"))
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)


def test_crawl_snyk():

    SNYK_DB_FILE = "../vulns_output/snyk_pip_vulns.csv"
    BASE_URL = "https://snyk.io/vuln/page/"
    SNYK_VULN_PAGE_BASE_URL = "https://snyk.io"

    total_vulns = 0
    first_page = 1
    last_page = 43

    vulnerabilities = []

    for i in range(first_page, last_page+1):
        vulns_list_url = BASE_URL + str(i) + "?type=pip"
        try:
            req = Request(vulns_list_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
        except (ValueError, URLError, HTTPError, ConnectionResetError):
            logging.info(f"Error opening page {i}")
        else:
            try:
                table = soup.findAll("tbody")[0]
            except Error:
                logging.info(f"Error getting vulnerabilities list")
                
            else:
                for vuln_row in table.findAll("tr"):
                    try:
                        severity = vuln_row.findAll("span")[0].getText().strip()
                        name = vuln_row.findAll("strong")[0].getText().strip()
                        vuln_url = SNYK_VULN_PAGE_BASE_URL + vuln_row.findAll("a")[0]["href"].strip()
                        if "/vuln/SNYK" not in vuln_url: vuln_url = ""
                        package_link = vuln_row.findAll("a")[1]
                        if "/vuln/pip:" not in package_link["href"]: package = ""
                        else: package = package_link.getText().strip()
                        versions = vuln_row.findAll("span", {"class": "semver"})[0].getText().strip()

                        if vuln_url != "":
                            try:
                                req = Request(vuln_url, headers={'User-Agent': 'Mozilla/5.0'})
                                soup = BeautifulSoup(urlopen(req).read(), features="html.parser")

                                cve = find_cve(soup)
                                github_advisory = find_ref_url("GitHub Advisory", soup)
                                github_commit = find_ref_url("GitHub Commit", soup)
                                github_release = find_ref_url("GitHub Release", soup)
                                github_release_tag = find_ref_url("GitHub Release Tag", soup)
                                github_add_inf = find_ref_url("GitHub Additional Information", soup)
                                github_pr = find_ref_url("GitHub PR", soup)
                                github_issue = find_ref_url("GitHub Issue", soup)
                                nvd = find_ref_url("NVD", soup)

                                vulnerabilities.append([severity, name, vuln_url, package, versions, cve,\
 github_advisory, github_commit, github_release, github_release_tag, github_add_inf, github_pr, github_issue, nvd])

                            except (ValueError, URLError, HTTPError, ConnectionResetError):
                                logging.info(f"Error opening vuln page")
                            
                    except KeyError:
                        logging.info(f"Error getting vulnerability data")

    logging.info(f"Tot vulns: {len(vulnerabilities)}")
    with open(SNYK_DB_FILE, mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        vulns_writer.writerow(['Severity', 'Name', 'Vulnerability_url', 'Package', 'Versions', 'CVE', 'GitHub Advisory', \
'GitHub Commit', 'GitHub Release', 'GitHub Release Tag', 'GitHub Additional Information', 'GitHub PR', 'GitHub Issue', 'NVD'])

        for i in range(0, len(vulnerabilities)):
            vulns_writer.writerow(vulnerabilities[i])

def find_cve(page: BeautifulSoup) -> str:
    for a in page.findAll("a"):
        cve = a.getText().strip()
        if "CVE-" in cve: return cve
    return ""

def find_ref_url(name: str, page: BeautifulSoup) -> str:
    for a in page.findAll("a"):
        if name == a.getText().strip(): return a["href"].strip()
    return ""