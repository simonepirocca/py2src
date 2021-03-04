"""
This file correlates commit link of a vulnerability with the relative hash, package name and directory
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
vulns_list_input_file = "../output/vulns_output/matching_vulns_unique_commit.csv"
old_vulns_output_file = "../output/vulns_output/old/clone_dir_from_commit_hash.csv"
output_file = "../output/vulns_output/clone_dir_from_commit_hash.csv"
#vulns_list_input_file = "../output/vulns_output/matching_vulns_unique_pr.csv"
#old_vulns_output_file = "../output/vulns_output/old/clone_dir_from_pr_commit_hash.csv"
#output_file = "../output/vulns_output/clone_dir_from_pr_commit_hash.csv"

vulns_list = {}
vulns = []

# Open vulns list csv file
with open(vulns_list_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            # For each vulnerability, put at index 'id' the related severity
            id = row[0]
            severity = row[1]
            vulns_list[id] = severity

        line_count += 1  

# Open old output csv file
with open(old_vulns_output_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            # Get Vuln ID, package name, clone directory and commit hash of each vulnerability
            id = row[0]
            name = row[1]
            clone_dir = row[2]

            commit_hash = row[3]
            #commit_url = row[3]
            #commit_hash = row[4]

            # If the vulnerability's id was present in the list
            # append the row including the severity
            if id in vulns_list:
                vulns.append([id, vulns_list[id], name, clone_dir, commit_hash])
                #vulns.append([id, vulns_list[id], name, clone_dir, commit_url, commit_hash])
            else: logger.info(f"Vulnerability '{id}' was not present in the vulns list")

        line_count += 1

# Store the information into a csv file
with open(output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Vuln ID', 'Severity', 'Package name', 'Clone dir', 'Commit hash'])
    #vulns_writer.writerow(['Vuln ID', 'Severity', 'Package name', 'Clone dir', 'Commit URL', 'Commit hash'])
    for i in range(0, len(vulns)):
        vulns_writer.writerow(vulns[i])