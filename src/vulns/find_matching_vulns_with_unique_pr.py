"""
This file finds the vulnerabilities related to already known packages and with PR link
"""
import sys
import os
import csv
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)


def test_find_matching_vulns_with_unique_pr():
    matching_vulns_with_pr = []
    tot_matching_vulns = 0

    with open('../../output/vulns_output/matching_vulns.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                commit_link = row[7]
                pr_link = row[11]
                if commit_link == "" and pr_link != "":
                    duplicated = False
                    for j in range (0, tot_matching_vulns):
                        if pr_link == matching_vulns_with_pr[j][11]:
                            duplicated = True
                            break
                    if not duplicated:
                        matching_vulns_with_pr.append(row)
                        tot_matching_vulns += 1

            line_count += 1

    logging.info(f"Matching vulns with unique PR: {len(matching_vulns_with_pr)}")

    with open("../../output/vulns_output/matching_vulns_unique_pr.csv", mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        vulns_writer.writerow(['Severity', 'Name', 'Vulnerability_url', 'Package', 'Versions', 'CVE', 'GitHub Advisory', \
'GitHub Commit', 'GitHub Release', 'GitHub Release Tag', 'GitHub Additional Information', 'GitHub PR', 'GitHub Issue', 'NVD'])

        for i in range(0, len(matching_vulns_with_pr)):
            vulns_writer.writerow(matching_vulns_with_pr[i])