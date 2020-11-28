"""
This file get all the missing metrics for each repo
"""
import sys
import os
import csv
from array import *
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)

def test_put_missing_urls():
    input_csv = "../../output/metrics_output/metrics_final_with_tags_and_0.csv"
    output_csv = "../../output/metrics_output/metrics_with_urls_added.csv"

    missing_urls = []
    packages = []
    inserted = 0
    not_found = 0
    not_corresponding = 0
    index = 0

    with open("../../output/metrics_output/missing_urls.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader: missing_urls.append(row[0])

    with open(input_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            metrics = []
            for i in range(0, 18):
                if i == 2 and row[i] == "":
                    if missing_urls[index] != "URL Not Found":
                        if row[0] not in missing_urls[index]:
                            not_corresponding += 1
                            logging.info(f"Name: {row[0]}, URL Found: {missing_urls[index]}")
                        row[i] = missing_urls[index]
                        inserted += 1
                    else:
                        logging.info(f"Name: {row[0]}, URL NOT Found")
                        not_found += 1
                    index += 1
                metrics.append(row[i])
            packages.append(metrics)

    logging.info(f"Inserted: {inserted}, Not found: {not_found}, Not Corresponding: {not_corresponding}")

    with open(output_csv, mode='w') as metrics_csv:
        packages_writer = csv.writer(metrics_csv, delimiter=';')
        packages_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars',\
 'last_commit', 'commit_freq', 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors',\
 'dep_repos', 'dep_pkgs', 'libraries_io_url', 'sourcerank', 'dep_repos', 'dep_pkgs'])

        for i in range(0, len(packages)):
            packages_writer.writerow(packages[i])