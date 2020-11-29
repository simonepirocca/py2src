"""
This file finds packages whose vulnerabilities have commit link
"""
import sys
import os
import csv
from urllib.request import Request, urlopen
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)


def test_find_commit_vulns():
    urls = {}
    commit_packages = []
    tot_commit_packages = 0

    with open('../../output/vulns_output/matching_packages.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                package_name = row[0]
                clone_url = row[1]

                urls[package_name] = clone_url

            line_count += 1 

    with open('../../output/vulns_output/matching_vulns_unique_commit.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                name = row[3]
                if name in urls:

                    duplicated = False
                    for j in range (0, tot_commit_packages):
                        if name == commit_packages[j][0]:
                            duplicated = True
                            break
                    if not duplicated:
                        commit_packages.append([name, urls[name]])
                        tot_commit_packages += 1

            line_count += 1

    logging.info(f"Commit packages: {tot_commit_packages}")

    with open("../../output/vulns_output/packages_with_vuln_commit.csv", mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        #vulns_writer.writerow(['Package name', 'Clone url'])
        for i in range(0, len(commit_packages)):
            vulns_writer.writerow(commit_packages[i])