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

from ..src.metrics.get_metrics import GetMetrics
from ..src.utils import log_function_output
#logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filepath="../logs/url_finder.log")
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/metrics.log")

# Set source, output and range
pypi_repos_json = "../inputs/top-pypi-packages-365-days.json"
old_metrics_input_file = "../output/metrics_output/metrics.csv"
input_file = "../output/metrics_output/github_urls_without_duplicates.csv"
output_file = "../output/metrics_output/metrics_values.csv"
start = 3001
count = 500
end = start + count

# Inizialize variables
old_old_metrics = {}
json_downloads = {}
metrics = []
json_packages = 0
old_urls_packages = 0
not_found_packages = 0
tot_packages = 0
rounds = 0

# Open old metrics csv file
with open(old_metrics_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            package_name = row[0]
            downloads = row[1]
            old_old_metrics[package_name] = downloads
        line_count += 1

# Open and decode the JSON file
with open(pypi_repos_json) as json_file:
    packages = json.load(json_file)["rows"]
    for i in range(0, len(packages)):
        # Get package name and downloads from the row
        package_name = packages[i]["project"]
        downloads = packages[i]["download_count"]
        json_downloads[package_name] = downloads

if start == 1:
    with open(output_file, mode='w') as csv_file:
        metrics_writer = csv.writer(csv_file, delimiter=';')
        metrics_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq',\
 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs'])

# Open the URL file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            package_name = row[0]
            github_url = row[1]
            downloads = 0

            if package_name in json_downloads:
                downloads = json_downloads[package_name]
                json_packages += 1
            elif package_name in old_old_metrics:
                downloads = old_old_metrics[package_name]
                old_urls_packages += 1
            else:
                not_found_packages += 1
                logger.info(f"Package '{package_name}' is not present in the JSON file")

            if github_url != "" and downloads != 0:
                # Get the metrics
                ms = GetMetrics(package_name, github_url)
                row_metrics = ms.get_metrics()

                # Put the metrics into the storage array
                package_metrics = [package_name, downloads, github_url]
                for metric in row_metrics: package_metrics.append(metric)
                metrics.append(package_metrics)
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
#logger.info(f"Total packages: {len(metrics)}, JSON: {json_packages}, OLD: {old_urls_packages}, NOT FOUND: {not_found_packages}")
with open(output_file, mode='a') as csv_file:
    metrics_writer = csv.writer(csv_file, delimiter=';')
#    metrics_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq',\
# 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs'])
    for i in range(0, len(metrics)):
        metrics_writer.writerow(metrics[i])