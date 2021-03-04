"""
This file finds packages whose vulnerabilities have PR link
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
packages_input_file = "../output/vulns_output/matching_packages.csv"
vulns_input_file = "../output/vulns_output/matching_vulns_unique_pr.csv"
output_file = "../output/vulns_output/packages_with_vuln_pr.csv"
urls = {}
pr_packages = []
tot_pr_packages = 0

# Open matching packages csv file
with open(packages_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            package_name = row[0]
            clone_url = row[1]
            # Put each package name and related clone URL into a dictionary
            urls[package_name] = clone_url

        line_count += 1 

# Open vulns csv file
with open(vulns_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # Get the package name related to that vulnerability
            name = row[4] # row[3] without Vuln ID column

            if name in urls:
                # If it is already known, append the package name and 
                # its clone url, if not already inserted
                duplicated = False
                for j in range (0, tot_pr_packages):
                    if name == pr_packages[j][0]:
                        duplicated = True
                        break
                if not duplicated:
                    pr_packages.append([name, urls[name]])
                    tot_pr_packages += 1

        line_count += 1

# Print out the number of packages whose vulns have a unique PR link
# and store the information into a csv file
logger.info(f"PR packages: {tot_pr_packages}")
with open(output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    #vulns_writer.writerow(['Package name', 'Clone url'])
    for i in range(0, len(pr_packages)):
        vulns_writer.writerow(pr_packages[i])