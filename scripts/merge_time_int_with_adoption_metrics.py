"""
This file merges the final time intervals of packages with the adoption metrics
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
metrics_input_file = "../output/metrics_final.csv"
time_intervals_input_file = "../output/vulns_final.csv"
output_file = "../output/vulns_output/time_interval_metrics_2.csv"
time_intervals = {}
packages = []

# Open time intervals csv file
with open(time_intervals_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            # Append each package to a dictionary, together with the row
            package_name = row[0]
            time_intervals[package_name] = row

        line_count += 1  

# Open metrics csv file
with open(metrics_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            # Get name and adoption metrics for each package
            name = row[0]
            pypi_downloads = row[1]
            commit_frequency = row[5]
            release_frequency = row[6]
            dep_repos = row[12]
            dep_packages = row[13]

            # If the vulnerability's package actually have some vulnerabilities 
            # with commit link associated, append it, its hash and the package directory
            if name in time_intervals:
                time_intervals_metrics = time_intervals[name]
                time_intervals_metrics.append(commit_frequency)
                time_intervals_metrics.append(release_frequency)
                time_intervals_metrics.append(pypi_downloads)
                time_intervals_metrics.append(dep_repos)
                time_intervals_metrics.append(dep_packages)

                packages.append(time_intervals_metrics)

        line_count += 1

# Store the information into a csv file
with open(output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(["Package name", "Clone dir", "Tot vulns", "Commit vulns", "PR vulns", "Tot Severity L", "Tot Severity M", "Tot Severity H",\
 "Median Severity", "Tot Major v.", "Tot Minor v.", "Tot Patch v.", "Median release type", "Commit time interval", "PR time interval", "Avg time interval",\
 "Commit frequency", "Release frequency", "Pypi downloads", "Dep repos", "Dep packages"])
    for i in range(0, len(packages)):
        vulns_writer.writerow(packages[i])