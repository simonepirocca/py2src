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
packages_input_file = "../output/metrics_final.csv"
vulns_input_file = "../output/vulns_output/snyk_pip_vulns.csv"
packages_output_file = "../output/vulns_output/matching_packages_with_vulns_count.csv"
urls = []
matching_packages = {}
matching_vulns = 0

# Open csv file of known packages
with open(packages_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # For each package retrieve the name and the clone URL,
            # starting from the GItHub URL, and put them in a dictionary
            package_name = row[0]
            github_url = row[2]
            last_char_i = len(github_url) - 1
            if github_url[last_char_i] == "/": clone_url = github_url[:last_char_i-1] + ".git"
            else: clone_url = github_url + ".git"

            urls.append(package_name)

        line_count += 1

# Open csv file of vulnerabilities
with open(vulns_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            name = row[3]

            if name in urls:
                matching_vulns += 1
                if name in matching_packages: matching_packages[name] += 1
                else: matching_packages[name] = 1

        line_count += 1

# Print out the total number of matching vulnerabilities and packages
logger.info(f"Matching vulns: {matching_vulns}, Matching packages: {len(matching_packages)}")

# Store matching packages
with open(packages_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Package name', '# Vulns'])
    for pkg in matching_packages:
        vulns_writer.writerow([pkg, matching_packages[pkg]])