"""
This file fixes the metrics where GitHub URL were wrong
"""
import sys
import os
import csv
import logging
import json
from urllib.request import Request, urlopen
import pytest
from pathlib import Path

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/metrics.log")

url_finder_module_path = Path().resolve() / "url_finder"
sys.path.append(str(url_finder_module_path))
from url_finder import URLFinder

get_metrics_module_path = Path().resolve() / "metrics"
sys.path.append(str(get_metrics_module_path))
from get_metrics import GetMetrics

# Set source, output and range
urls_input_file = "../output/metrics_output/github_urls_without_duplicates.csv"
old_metrics_input_file = "../output/metrics_output/metrics.csv"
metrics_input_file = "../output/metrics_final.csv"
output_file = "../output/metrics_output/metrics_fixed_on_right_urls.csv"
start = 1
count = 1000
end = start + count

# Inizialize variables
total_metrics = []
old_old_metrics = {}
old_metrics = {}
correct_rows = 0
wrong_rows = 0
not_before_rows = 0

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

# Open metrics csv file
with open(metrics_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            package_name = row[0]
            old_metrics[package_name] = row
        line_count += 1

if start == 1:
    with open(output_file, mode='w') as csv_file:
        metrics_writer = csv.writer(csv_file, delimiter=';')
        metrics_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq',\
     'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs'])

# Open the urls file
with open(urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # row = [package_name, github_url]
            package_name = row[0]
            final_url = row[1]

            # If the package exists and the GitHub URL is not changed, simply append the row
            if package_name in old_metrics:
                metrics_url = URLFinder.real_github_url(old_metrics[package_name][2])
                if metrics_url == final_url:
                    package_metrics = []
                    for i in range (0, 14): package_metrics.append(old_metrics[package_name][i])
                    total_metrics.append(package_metrics)
                    correct_rows += 1
                else:
                    downloads = old_metrics[package_name][1]
                    # Get the metrics
                    ms = GetMetrics(package_name, final_url)
                    metrics = ms.get_metrics()

                    # Put the metrics into the storage array
                    package_metrics = [package_name, downloads, final_url]
                    for metric in metrics: package_metrics.append(metric)
                    total_metrics.append(package_metrics)
                    wrong_rows += 1
                    #logger.info(f"{line_count}. Wrong row: '{package_name}' with URL '{metrics_url}'")
            else:
                downloads = old_old_metrics[package_name]
                # Get the metrics
                ms = GetMetrics(package_name, final_url)
                metrics = ms.get_metrics()

                # Put the metrics into the storage array
                package_metrics = [package_name, downloads, final_url]
                for metric in metrics: package_metrics.append(metric)
                total_metrics.append(package_metrics)
                not_before_rows += 1
                #logger.info(f"{line_count}. Package '{package_name}' not present before")

        if len(total_metrics) % 200 == 0 and line_count > start: logger.info(f"rows: {len(total_metrics)}")
        line_count += 1
        if line_count >= end: break

#not_in_urls_metrics = len(old_metrics) - correct_rows - wrong_rows

# Print out the information and store the metrics
#logger.info(f"Len old old metrics: {len(old_old_metrics)}, Len old metrics: {len(old_metrics)}, Len final metrics: {len(total_metrics)}")
logger.info(f"Correct rows: {correct_rows}, Wrong rows: {wrong_rows}, Not before rows: {not_before_rows}")
with open(output_file, mode='a') as csv_file:
    metrics_writer = csv.writer(csv_file, delimiter=';')
#    metrics_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq',\
# 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs'])
    for i in range(0, len(total_metrics)):
        metrics_writer.writerow(total_metrics[i])