"""
This file finds the vulnerabilities related to already known packages and with commit link
"""
import sys
import os
import csv
import logging
import pytest
from pathlib import Path

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/vulns.log")

# Set input and output files, inizialize variables
input_file = "../output/vulns_output/matching_vulns.csv"
output_file = "../output/vulns_output/matching_vulns_unique_commit.csv"
matching_vulns_with_commit = []
tot_matching_vulns = 0

# Open csv file of vulnerabilities
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # Get the commit link
            commit_link = row[7]
            # If it is nor empty or already present, append the vulnerability
            if commit_link != "":
                duplicated = False
                for j in range (0, tot_matching_vulns):
                    if commit_link == matching_vulns_with_commit[j][7]:
                        duplicated = True
                        break
                if not duplicated:
                    matching_vulns_with_commit.append(row)
                    tot_matching_vulns += 1

        line_count += 1

# Print out the number of vulns with unique commit link and store the information into a csv file
logger.info(f"Matching vulns with unique commit: {len(matching_vulns_with_commit)}")
with open(output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Severity', 'Name', 'Vulnerability_url', 'Package', 'Versions', 'CVE', 'GitHub Advisory', \
'GitHub Commit', 'GitHub Release', 'GitHub Release Tag', 'GitHub Additional Information', 'GitHub PR', 'GitHub Issue', 'NVD'])
    for i in range(0, len(matching_vulns_with_commit)):
        vulns_writer.writerow(matching_vulns_with_commit[i])