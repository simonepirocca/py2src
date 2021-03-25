"""
This file finds the vulnerabilities related to already known packages,
storing them and the packages involved. 
If indicated, it also counts the number of unique occurrences 
related to a certain reference
"""
import sys
import os
import csv
import logging
import pytest
from pathlib import Path

from ..src.utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/vulns.log")

# Set input and output files, inizialize variables
packages_input_file = "../output/vulns_output/packages_asc.csv"
vulns_input_file = "../output/vulns_output/snyk_pip_vulns.csv"
packages_output_file = "../output/vulns_output/matching_packages.csv"
vulns_output_file = "../output/vulns_output/matching_vulns.csv"
urls = {}
matching_vulns = []
matching_packages = []
tot_matching_packages = 0

ref_to_check = ""
ref_column = 0
ref_vulns = []
ref_packages = []
tot_ref_packages = 0
tot_ref_vulns = 0

# Open csv file of known packages
with open(packages_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # For each package retrieve the name and the clone URL,
            # starting from the GItHub URL, and put them in a dictionary
            package_name = row[0]
            github_url = row[1]
            last_char_i = len(github_url) - 1
            if github_url[last_char_i] == "/": clone_url = github_url[:last_char_i-1] + ".git"
            else: clone_url = github_url + ".git"

            urls[package_name] = clone_url

        line_count += 1

# Open csv file of vulnerabilities
with open(vulns_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            name = row[3]

            # If the package name related to the vulnerability is known ...
            if name in urls:
                #... append the matching vulnerability...
                matching_vulns.append(row)

                #... and append the matching package, if not already in the list
                duplicated = False
                for j in range (0, tot_matching_packages):
                    if name == matching_packages[j][0]:
                        duplicated = True
                        break
                if not duplicated:
                    matching_packages.append([name, urls[name]])
                    tot_matching_packages += 1

                # If there is a reference to count, do the same,
                # checking also that the reference value is unique
                if ref_to_check != "" and row[ref_column] != "":
                    ref_info = row[ref_column]

                    duplicated = False
                    for j in range (0, tot_ref_vulns):
                        if ref_info == ref_vulns[j][ref_column]:
                            duplicated = True
                            break
                    if not duplicated:
                        ref_vulns.append(row)
                        tot_ref_vulns += 1

                        duplicated = False
                        for j in range (0, tot_ref_packages):
                            if name == ref_packages[j][0]:
                                duplicated = True
                                break
                        if not duplicated:
                            ref_packages.append([name, urls[name]])
                            tot_ref_packages += 1

        line_count += 1

# Print out the total number of matching vulnerabilities and packages
logger.info(f"Matching vulns: {len(matching_vulns)}, Matching packages: {tot_matching_packages}")
if ref_to_check != "":
    logger.info(f"'{ref_to_check}' vulns: {tot_ref_vulns}, '{ref_to_check}' packages: {tot_ref_packages}")

# Store matching vulnerabilities
with open(vulns_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Severity', 'Name', 'Vulnerability_url', 'Package', 'Versions', 'CVE', 'GitHub Advisory', \
'GitHub Commit', 'GitHub Release', 'GitHub Release Tag', 'GitHub Additional Information', 'GitHub PR', 'GitHub Issue', 'NVD'])
    for i in range(0, len(matching_vulns)):
        vulns_writer.writerow(matching_vulns[i])

# Store matching packages
with open(packages_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Package name', 'Clone url'])
    for i in range(0, len(matching_packages)):
        vulns_writer.writerow(matching_packages[i])