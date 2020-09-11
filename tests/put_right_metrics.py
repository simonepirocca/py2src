"""
This file get all the missing metrics for each repo
"""
import sys
import os
import csv
import json
from array import *
from datetime import date
from urllib.request import Request, urlopen
sys.path.append(os.path.abspath("../src/"))
from package import Package
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)

def test_put_right_metrics():

    right_metrics = []
    not_first_line = False
    with open("../metrics_output/metrics_final_only_wrong_urls_fixed.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if not_first_line:
                tmp_metrics = []
                for i in range(0, 13): tmp_metrics.append(row[i])
                right_metrics.append(tmp_metrics)
            else: not_first_line = True

    logging.info(f"Right metrics len: {len(right_metrics)}")

    start = 1
    count = 4000
    end = start + count

    index = 0

    input_csv = "../metrics_output/metrics_final_with_wrong_urls.csv"
    output_csv = "../metrics_output/metrics_final.csv"

    packages = []
    missing_github_url = 0
    complete_rows = 0
    semi_complete_rows = 0
    tot_packages = 0
    duplicates = 0
    line_count = 0

    with open(input_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if line_count >= start:
                metrics = []
                if index < len(right_metrics) and row[0] == right_metrics[index][0]:
                    for i in range(0, 2): metrics.append(row[i])
                    for i in range(1, 13): metrics.append(right_metrics[index][i])
                    for i in range(14, 18): metrics.append(row[i])
                    index += 1
                else: 
                    for i in range(0, 18): metrics.append(row[i])

                packages.append(metrics)
                tot_packages += 1

            line_count += 1
            if line_count >= end: break


    with open(output_csv, mode='w') as metrics_csv:
        packages_writer = csv.writer(metrics_csv, delimiter=';')
        packages_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars',\
 'last_commit', 'commit_freq', 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors',\
 'dep_repos', 'dep_pkgs', 'libraries_io_url', 'sourcerank', 'dep_repos', 'dep_pkgs'])

        for i in range(0, tot_packages):
            packages_writer.writerow(packages[i])

    logging.info(f"Changed rows: {index}, Total packages: {tot_packages}")