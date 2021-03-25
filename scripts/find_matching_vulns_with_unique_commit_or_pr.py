"""
This file finds the vulnerabilities related to already known packages and with commit link
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
packages_input_file = "../output/vulns_output/matching_packages.csv"
input_file = "../output/vulns_output/matching_vulns.csv"
vulns_commit_output_file = "../output/vulns_output/matching_vulns_unique_commit.csv"
packages_commit_output_file = "../output/vulns_output/packages_with_vuln_commit.csv"
vulns_pr_output_file = "../output/vulns_output/matching_vulns_unique_pr.csv"
packages_pr_output_file = "../output/vulns_output/packages_with_vuln_pr.csv"
packages_to_clone_output_file = "../output/vulns_output/packages_to_clone.csv"

# Inizialize variables
urls = {}
commit_vulns = []
commit_packages = []
packages_to_clone = []
tot_commit_vulns = 0
tot_commit_packages = 0
pr_vulns = []
pr_packages = []
tot_pr_vulns = 0
tot_pr_packages = 0
tot_to_clone = 0

# Open matching packages csv file
with open(packages_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            package_name = row[0]
            clone_url = row[1]
            # Put each package name and related clone URL into a dictionary
            urls[package_name] = clone_url
        line_count += 1 

# Open csv file of vulnerabilities
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # Get the package name and commit link
            package_name = row[3]
            commit_link = row[7]
            pr_link = row[11]
            # If it is nor empty or already present, append the vulnerability
            if commit_link != "":
                vuln_duplicated = False
                for j in range (0, tot_commit_vulns):
                    if commit_link == commit_vulns[j][7]:
                        vuln_duplicated = True
                        break
                if not vuln_duplicated:
                    commit_vulns.append(row)
                    tot_commit_vulns += 1

                    # If it is not already present, append the package
                    pkg_duplicated = False
                    for k in range (0, tot_commit_packages):
                        if package_name == commit_packages[k][0]:
                            pkg_duplicated = True
                            break
                    if not pkg_duplicated:
                        commit_packages.append([package_name, urls[package_name]])
                        tot_commit_packages += 1

                        # If it is not already present, append the package to the ones to clone
                        clone_duplicated = False
                        for y in range (0, tot_to_clone):
                            if package_name == packages_to_clone[y][0]:
                                clone_duplicated = True
                                break
                        if not clone_duplicated:
                            packages_to_clone.append([package_name, urls[package_name]])
                            tot_to_clone += 1

            elif pr_link != "":
                vuln_duplicated = False
                for j in range (0, tot_pr_vulns):
                    if pr_link == pr_vulns[j][7]:
                        vuln_duplicated = True
                        break
                if not vuln_duplicated:
                    pr_vulns.append(row)
                    tot_pr_vulns += 1

                    # If it is not already present, append the package
                    pkg_duplicated = False
                    for k in range (0, tot_pr_packages):
                        if package_name == pr_packages[k][0]:
                            pkg_duplicated = True
                            break
                    if not pkg_duplicated:
                        pr_packages.append([package_name, urls[package_name]])
                        tot_pr_packages += 1

                        # If it is not already present, append the package to the ones to clone
                        clone_duplicated = False
                        for y in range (0, tot_to_clone):
                            if package_name == packages_to_clone[y][0]:
                                clone_duplicated = True
                                break
                        if not clone_duplicated:
                            packages_to_clone.append([package_name, urls[package_name]])
                            tot_to_clone += 1

        line_count += 1

# Print out the number of vulns with unique commit link and store the information into a csv file
logger.info(f"Commit vulns: {len(commit_vulns)}, Commit packages: {len(commit_packages)}")
logger.info(f"PR vulns: {len(pr_vulns)}, PR packages: {len(pr_packages)}, Packages to clone: {len(packages_to_clone)}")

with open(vulns_commit_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Severity', 'Name', 'Vulnerability_url', 'Package', 'Versions', 'CVE', 'GitHub Advisory', \
'GitHub Commit', 'GitHub Release', 'GitHub Release Tag', 'GitHub Additional Information', 'GitHub PR', 'GitHub Issue', 'NVD'])
    for i in range(0, len(commit_vulns)):
        vulns_writer.writerow(commit_vulns[i])

with open(packages_commit_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Package name', 'Clone url'])
    for i in range(0, len(commit_packages)):
        vulns_writer.writerow(commit_packages[i])

with open(vulns_pr_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Severity', 'Name', 'Vulnerability_url', 'Package', 'Versions', 'CVE', 'GitHub Advisory', \
'GitHub Commit', 'GitHub Release', 'GitHub Release Tag', 'GitHub Additional Information', 'GitHub PR', 'GitHub Issue', 'NVD'])
    for i in range(0, len(pr_vulns)):
        vulns_writer.writerow(pr_vulns[i])

with open(packages_pr_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Package name', 'Clone url'])
    for i in range(0, len(pr_packages)):
        vulns_writer.writerow(pr_packages[i])

with open(packages_to_clone_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Package name', 'Clone url'])
    for i in range(0, len(packages_to_clone)):
        vulns_writer.writerow(packages_to_clone[i])