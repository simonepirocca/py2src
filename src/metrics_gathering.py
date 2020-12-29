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

get_metrics_module_path = Path().resolve() / "metrics"
sys.path.append(str(get_metrics_module_path))
from get_metrics import GetMetrics

# Set source, output and range
input_file = "../output/url_finder_output/github_urls.csv"
output_file = "../output/metrics_output/metrics_values.csv"
total_metrics = []

# Open the URL file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    next(csv_reader, None) # Skip header
    for row in csv_reader:
        # row = [package_name, github_url, accuracy, pypi_downloads]
        package_name = row[0]
        github_url = row[1]
        downloads = row[3]

        # Get the metrics
        ms = GetMetrics(package_name, github_url)
        metrics = ms.get_metrics()

        # Put the metrics into the storage array
        package_metrics = [package_name, downloads, github_url]
        for metric in metrics: package_metrics.append(metric)
        total_metrics.append(package_metrics)

# Store the metrics
with open(output_file, mode='w') as csv_file:
    metrics_writer = csv.writer(csv_file, delimiter=';')
    metrics_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq',\
 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs'])
    for i in range(0, len(total_metrics)):
        metrics_writer.writerow(total_metrics[i])