"""
This file get the metrics'values from a list of package URLs
"""
import sys
import os
import csv
import logging
import json
from urllib.request import Request, urlopen
import pytest
from pathlib import Path

from ..src.metrics.metrics import Metrics
from ..src.utils import log_function_output
#logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filepath="../logs/url_finder.log")
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/metrics.log")

# Set source, output and range
input_file = "../output/metrics_output/metrics_with_licenses.csv"
output_file = "../output/metrics_output/metrics_with_licenses_2.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
metrics = []
valid_licenses = {}
other_licenses = {}
text_licenses = {}
error_licenses = {}
other = {}
tot_packages = 0

valid_licenses_array = ["MIT License", "Apache-2.0 License", "BSD-3-Clause License", "BSD-2-Clause License", "ISC License"]
other_licenses_array = ["LGPL-2.1 License", "LGPL-3.0 License", "GPL-2.0 License", "GPL-3.0 License", "MPL-2.0 License",\
 "EPL-1.0 License", "WTFPL License", "CC0-1.0 License", "AGPL-3.0 License", "0BSD License", "BSL-1.0 License", "Unlicense License"]
error_licenses_array = ["License not found", "Error opening GitHub repository", "Error getting the license link", "Error opening license link"]

#if start == 1:
#    with open(output_file, mode='w') as csv_file:
#        metrics_writer = csv.writer(csv_file, delimiter=';')
#        metrics_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq', 'release_freq',\
# 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs', 'vulns', 'license'])

# Open the URL file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            package_name = row[0]
            github_url = row[2]
            license = row[15]
            if line_count < 2000 and (license == "License not found" or license == "Different license found"):
                pkg = Metrics(package_name, github_url)
                license = pkg.get_license_from_github_repo()
                row[15] = license
            #for strange_license in error_licenses_array:
            #    if license == strange_license: logger.info(f"{line_count}. '{package_name}' --> {strange_license}")

            if license in valid_licenses_array:
                if license in valid_licenses: valid_licenses[license] += 1
                else: valid_licenses[license] = 1
            elif license in other_licenses_array:
                if license in other_licenses: other_licenses[license] += 1
                else: other_licenses[license] = 1
            elif "(text)" in license:
                if license in text_licenses: text_licenses[license] += 1
                else: text_licenses[license] = 1
            elif license in error_licenses_array:
                if license in error_licenses: error_licenses[license] += 1
                else: error_licenses[license] = 1
            else:
                if license in other: other[license] += 1
                else: other[license] = 1

            tmp_metrics = row
            #tmp_metrics.append(license)
            metrics.append(tmp_metrics)
            tot_packages += 1

        if tot_packages % 100 == 0 and tot_packages > 0:
            logger.info(f"rows: {tot_packages}")
            #with open(output_file, mode='a') as csv_file:
            #    metrics_writer = csv.writer(csv_file, delimiter=';')
            #    for i in range(len(metrics) - 100, len(metrics)):
            #        metrics_writer.writerow(metrics[i])
        line_count += 1
        if line_count >= end: break

# Print out the number of packages and store the metrics
logger.info(f"----------------------------------------------  Total packages: {len(metrics)}  ---------------------------------------------------")
logger.info(f"Valid Licenses: {valid_licenses}")
logger.info(f"Other Licenses: {other_licenses}")
logger.info(f"Text Licenses: {text_licenses}")
logger.info(f"Not Found Licenses: {error_licenses}")
logger.info(f"Other: {other}")
logger.info(f"-----------------------------------------------------------------------------------------------------------------------------------------")
with open(output_file, mode='w') as csv_file:
    metrics_writer = csv.writer(csv_file, delimiter=';')
    metrics_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq', 'release_freq',\
 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs', 'vulns', 'license'])
    for i in range(0, len(metrics)):
        metrics_writer.writerow(metrics[i])