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
input_file = "../output/metrics_output/metrics_with_licenses_2.csv"
output_file = "../output/metrics_output/metrics_with_licenses_3.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
metrics = []
tot_permissive = 0
tot_copyleft = 0
tot_unknown = 0
tot_packages = 0

permissive_license_types = ["MIT License", "Apache-2.0 License", "BSD-3-Clause License", "BSD-2-Clause License", "ISC License", "Unlicense License",\
 "CC0-1.0 License", "WTFPL License", "0BSD License", "BSL-1.0 License", "Apache License (text)", "MIT License (text)", "Python Software Foundation (text)",\
 "Modified BSD License (text)", "BSD 3-Clause License (text)", "Expat License (text)", "ISC License (text)", "BSD 2-Clause License (text)", "HPND License (text)"]
copyleft_license_types = ["GPL-3.0 License", "LGPL-3.0 License", "GPL-2.0 License", "LGPL-2.1 License", "AGPL-3.0 License", "MPL-2.0 License", "EPL-1.0 License",\
 "LGPL (text)", "EPL (text)", "Mozilla Public License (text)", "CDDL (text)", "AGPL (text)"]

# Open the URL file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            package_name = row[0]
            github_url = row[2]
            license = row[15]

            if license in permissive_license_types:
                tot_permissive += 1
                license = 1
                row[15] = license
            elif license in copyleft_license_types:
                tot_copyleft += 1
                license = -1
                row[15] = license
            else:
                tot_unknown += 1
                license = 0
                row[15] = license

            tmp_metrics = row
            metrics.append(tmp_metrics)
            tot_packages += 1

        line_count += 1
        if line_count >= end: break

# Print out the number of packages and store the metrics
logger.info(f"----------------------------------------------  Total packages: {len(metrics)}  ---------------------------------------------------")
logger.info(f"Tot Permissive Licenses: {tot_permissive}, Tot Copyleft Licenses: {tot_copyleft}, Tot Unknown Licenses: {tot_unknown}")
logger.info(f"-----------------------------------------------------------------------------------------------------------------------------------------")
with open(output_file, mode='w') as csv_file:
    metrics_writer = csv.writer(csv_file, delimiter=';')
    metrics_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq', 'release_freq',\
 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs', 'vulns', 'license'])
    for i in range(0, len(metrics)):
        metrics_writer.writerow(metrics[i])