import sys
import os
import csv
import logging
import json
from urllib.request import Request, urlopen
from datetime import date
import pytest
from pathlib import Path


url_finder_module_path = Path().resolve().parent / "src" / "url_finder"
sys.path.append(str(url_finder_module_path))
from url_finder import URLFinder

get_metrics_module_path = Path().resolve().parent / "src" / "metrics"
sys.path.append(str(get_metrics_module_path))
from get_metrics import GetMetrics

utils_module_path = Path().resolve().parent / "src" / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/metrics.log")

# Test the GitHub URL gathering of a package, using three sources
def test_metrics_gathering():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'

    ms = GetMetrics(package_name, github_url)
    metrics = ms.get_metrics()

    # Log the metrics
    logger.info(f"{metrics}")

# Test metrics gathering for a list of packages
def test_metrics_of_list_of_packages():
    # Set source, output and range
    pypi_repos_json = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-365-days.json"
    output_file = "../output/metrics_output/metrics.csv"
    start = 1
    count = 1
    end = start + count

#    if start == 1:
#        with open(output_file, mode='w') as packages:
#            packages_writer = csv.writer(packages, delimiter=';')
#            packages_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars', 'last_commit', 'commit_freq',\
# 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors', 'dep_repos', 'dep_pkgs'])

    with urlopen(pypi_repos_json) as response:
        repos = json.loads(response.read().decode())["rows"]
        for i in range(start, end):
            # Get package name and downloads from json
            package_name = repos[i-1]["project"]
            downloads = repos[i-1]["download_count"]

            # Get GitHub URL
            url_finder = URLFinder(package_name)
            github_url = url_finder.find_github_url_from_pypi_page()

            # Get the metrics
            ms = GetMetrics(package_name, github_url)
            metrics = ms.get_metrics()

            # Put the metrics into the storage array
            csv = [package_name, downloads, github_url]
            for metric in metrics: csv.append(metric)

            # Save the line into the file
            logger.info(f"{csv}")
            #with open(output_file, mode='w') as packages:
            #    packages_writer = csv.writer(packages, delimiter=';')
            #    packages_writer.writerow(csv)
            break # to test just one line