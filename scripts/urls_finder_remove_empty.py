"""
This file separate duplicates (with the same GitHub URL) from the 4000 packages csv file
"""
import json
import sys
import os
import csv
import logging
import pytest
from urllib.request import Request, urlopen
from pathlib import Path

from ..src.utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/vulns.log")

# Set source and range
metrics_input_file = "../output/metrics_final.csv"
input_file = "../output/url_finder_final.csv"
output_file = "../output/vulns_output/packages_asc.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
metrics = {}
urls = []
url_index = 39

# Open old metrics csv file
with open(metrics_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            github_url = row[2]
            metrics[github_url] = [row[1], row[12], row[13]]
        line_count += 1

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get accuracy and three GitHub URLs with the final one from the row
            package_name = row[0]
            github_url = row[url_index]
            if github_url != "" :
                if github_url in metrics:
                    pypi_downloads = metrics[github_url][0]
                    dep_repos = metrics[github_url][1]
                    dep_pkgs = metrics[github_url][2]
                    urls.append([package_name, github_url, pypi_downloads, dep_repos, dep_pkgs])
                else: logger.info(f"{line_count}. Can't find package: {package_name}")

        line_count += 1
        if line_count > end: break

# Print out and store the information
logger.info(f"Not Empty URLs: {len(urls)}")
with open(output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["package_name", "github_url", "pypi_downloads", "dep_repos", "dep_pkgs"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])