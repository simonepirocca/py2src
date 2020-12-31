"""
This file crawls snyk database to retrieve all the pip vulnerabilities
"""
import sys
import os
import csv
from bs4 import BeautifulSoup
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
import logging
import pytest
from pathlib import Path

vulns_module_path = Path().resolve() / "vulns"
sys.path.append(str(vulns_module_path))
from vulns import Vuln

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/vulns.log")

# Set input file and page range, initialize variables
SNYK_DB_FILE = "../output/vulns_output/snyk_pip_vulns.csv"
BASE_URL = "https://snyk.io/vuln/page/"
SNYK_VULN_PAGE_BASE_URL = "https://snyk.io"
total_vulns = 0
first_page = 1
last_page = 5 # 43 is the last current page
vulnerabilities = []

# Loop among pages
for i in range(first_page, last_page+1):
    vulns_list_url = BASE_URL + str(i) + "?type=pip"
    try:
        req = Request(vulns_list_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
    except (ValueError, URLError, HTTPError, ConnectionResetError):
        logger.info(f"Error opening page {i}")
    else:
        try:
            # Get the list of vulnerabilities, if it exists
            table = soup.findAll("tbody")[0]
        except Error:
            logger.info(f"Error getting vulnerabilities list")
        else:
            for vuln_row in table.findAll("tr"):
                try:
                    # For each vulnerability, try to gather its name, the severity, the URL,
                    # the related package name and the affected version from the row information
                    severity = vuln_row.findAll("span")[0].getText().strip()
                    name = vuln_row.findAll("strong")[0].getText().strip()
                    vuln_url = SNYK_VULN_PAGE_BASE_URL + vuln_row.findAll("a")[0]["href"].strip()
                    if "/vuln/SNYK" not in vuln_url: vuln_url = ""
                    package_link = vuln_row.findAll("a")[1]
                    if "/vuln/pip:" not in package_link["href"]: package = ""
                    else: package = package_link.getText().strip()
                    versions = vuln_row.findAll("span", {"class": "semver"})[0].getText().strip()

                    # If the URL is not empty, retrieve all the reference URL related to the vulnerability
                    if vuln_url != "":
                        vuln_info = Vuln(vuln_url).get_snyk_vuln_info()
                        # If at least one information has been found, 
                        # create the final array and append it as new vulnerability
                        if vuln_info != "":
                            info = [severity, name, vuln_url, package, versions]
                            for data in vuln_info: info.append(data)
                            vulnerabilities.append(info)

                except KeyError:
                    logger.info(f"Error getting vulnerability data")

# Print out the number of vulnerabilities found and store the information in a CSV file
logger.info(f"Tot SKYK vulns: {len(vulnerabilities)}")
with open(SNYK_DB_FILE, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Severity', 'Name', 'Vulnerability_url', 'Package', 'Versions', 'CVE', 'GitHub Advisory', \
'GitHub Commit', 'GitHub Release', 'GitHub Release Tag', 'GitHub Additional Information', 'GitHub PR', 'GitHub Issue', 'NVD'])
    for i in range(0, len(vulnerabilities)): vulns_writer.writerow(vulnerabilities[i])