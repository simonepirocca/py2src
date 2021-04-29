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
urls = {}
matching_vulns = []
matching_packages = []
tot_matching_packages = 0

ref_to_check = ""
all_packages = []
match_packages = []
ref_column = 0
ref_match_vulns = []
ref_match_packages = []
ref_vulns = []
ref_packages = []
tot_ref_match_packages = 0
tot_ref_match_vulns = 0
tot_ref_packages = 0
tot_ref_vulns = 0
tot_ref_match_vulns_with_dupl = 0
tot_ref_vulns_with_dupl = 0
tot_match_vulns = 0
tot_vulns = 0
tot_match_vulns = 0
tot_packages = 0
tot_match_packages = 0

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

            if ref_to_check != "" and row[ref_column] != "":
                ref_info = row[ref_column]

                if name in urls:
                    tot_ref_match_vulns_with_dupl += 1
                    if ref_info not in ref_match_vulns:
                        ref_match_vulns.append(ref_info)
                        tot_ref_match_vulns += 1

                    if name not in ref_match_packages:
                        ref_match_packages.append(name)
                        tot_ref_match_packages += 1

                tot_ref_vulns_with_dupl += 1
                if ref_info not in ref_vulns:
                    ref_vulns.append(ref_info)
                    tot_ref_vulns += 1

                if name not in ref_packages:
                    ref_packages.append(name)
                    tot_ref_packages += 1

            else:
                tot_vulns += 1
                if name not in all_packages:
                    all_packages.append(name)
                    tot_packages += 1

                if name in urls:
                    tot_match_vulns += 1
                    if name not in match_packages:
                        match_packages.append(name)
                        tot_match_packages += 1


        line_count += 1

# Print out the total number of matching vulnerabilities and packages
if ref_to_check != "":
    logger.info(f"'{ref_to_check}' MATCHING vulns: {tot_ref_match_vulns} (no dupl.: {tot_ref_match_vulns_with_dupl}), MATCHING packages: {tot_ref_match_packages}")
    logger.info(f"'{ref_to_check}' TOTAL vulns: {tot_ref_vulns} (no dupl.: {tot_ref_vulns_with_dupl}), TOTAL packages: {tot_ref_packages}")
else:
    logger.info(f"TOTAL vulns: {tot_vulns} (PACKAGES: {tot_packages}), MATCHING vulns: {tot_match_vulns} (PACKAGES: {tot_match_packages})")
