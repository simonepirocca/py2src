"""
This file finds the vulnerabilities related to already known packages
"""
import sys
import os
import csv
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)


def test_match_packages():
    urls = {}
    matching_vulns = []
    matching_packages = []
    tot_matching_packages = 0

    with open('../../output/metrics_output/packages_asc.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                package_name = row[0]
                github_url = row[1]
                last_char_i = len(github_url) - 1
                if github_url[last_char_i] == "/": clone_url = github_url[:last_char_i-1] + ".git"
                else: clone_url = github_url + ".git"

                urls[package_name] = clone_url

            line_count += 1

    with open('../../output/vulns_output/snyk_pip_vulns.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                name = row[3]
                if name in urls:
                    matching_vulns.append(row)

                    duplicated = False
                    for j in range (0, tot_matching_packages):
                        if name == matching_packages[j][0]:
                            duplicated = True
                            break
                    if not duplicated:
                        matching_packages.append([name, urls[name]])
                        tot_matching_packages += 1

            line_count += 1

    logging.info(f"Matching vulns: {len(matching_vulns)}, Matching packages: {tot_matching_packages}")

    with open("../../output/vulns_output/matching_vulns.csv", mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        vulns_writer.writerow(['Severity', 'Name', 'Vulnerability_url', 'Package', 'Versions', 'CVE', 'GitHub Advisory', \
'GitHub Commit', 'GitHub Release', 'GitHub Release Tag', 'GitHub Additional Information', 'GitHub PR', 'GitHub Issue', 'NVD'])

        for i in range(0, len(matching_vulns)):
            vulns_writer.writerow(matching_vulns[i])

    with open("../../output/vulns_output/matching_packages.csv", mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        vulns_writer.writerow(['Package name', 'Clone url'])
        for i in range(0, len(matching_packages)):
            vulns_writer.writerow(matching_packages[i])