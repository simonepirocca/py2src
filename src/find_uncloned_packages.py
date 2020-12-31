"""
This file finds the uncloned packages
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
input_file = "../output/vulns_output/packages_with_vuln_pr.csv"
output_file = "../output/vulns_output/test_uncloned_pr_packages.csv"
uncloned_packages = []

# Open csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            # For each package, get the name and clone URL, extracting the clone directory
            package_name = row[0]
            clone_url = row[1]
            clone_dir = clone_url.split("/")[-1]
            clone_dir = clone_dir.replace(".git", "")

            # If the related directory is not present, append as uncloned package
            if not os.path.isdir("../cloned_packages/" + clone_dir):
                logger.info(f"Package '{package_name}' is not in directory {clone_dir}'")
                uncloned_packages.append([package_name, clone_url, clone_dir])

        line_count += 1  

# Store the uncloned packages into a csv file
with open(output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Package name', 'Clone url', 'Clone dir'])
    for i in range(0, len(uncloned_packages)):
        vulns_writer.writerow(uncloned_packages[i])