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
input_file = "../output/metrics_final.csv"
vulns_input_file = "../output/vulns_output/matching_packages_with_vulns_count.csv"
output_file = "../output/metrics_output/metrics_with_vulns.csv"
vulns = {}
metrics = []
packages_with_vulns = 0

# Open csv file of known vulnerabilities
with open(vulns_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            vulns[row[0]] = row[1]
        line_count += 1

# Open csv file of metrics
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            package_name = row[0]

            if package_name in vulns:
                row.append(vulns[package_name])
                packages_with_vulns += 1
            else: row.append(0)

            metrics.append(row)

        line_count += 1

# Print out the total number of matching vulnerabilities and packages
logger.info(f"Total URLs: {len(metrics)}, Packages with vulns: {packages_with_vulns}")

# Store information
with open(output_file, mode='w') as csv_file:
    metrics_writer = csv.writer(csv_file, delimiter=';')
    metrics_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq', 'release_freq',\
 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs', 'vulns'])
    for i in range(0, len(metrics)):
        metrics_writer.writerow(metrics[i])