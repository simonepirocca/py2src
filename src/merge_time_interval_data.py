"""
This file merges the CSV files containing time intervals data about 
single vulnerabilities and package summaries, obtained from Commit and PR vulnerabilities
"""
import sys
import os
import csv
import logging
import pytest
from pathlib import Path

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/vulns.log")

# Set input and output files, inizialize variables
input_commit_vuln_file = "../output/vulns_output/commit_vulns_time_interval.csv"
input_pr_vuln_file = "../output/vulns_output/pr_vulns_time_interval.csv"
input_commit_packages_file = "../output/vulns_output/package_time_interval_for_commits_vulns.csv"
input_pr_packages_file = "../output/vulns_output/package_time_interval_for_pr_vulns.csv"
vulns_output_file = "../output/vulns_output/final_vulns_time_intervals.csv"
packages_output_file = "../output/vulns_output/final_packages_time_intervals.csv"

vulns = []
packages = []

# Open csv file of commit vulnerabilities
with open(input_commit_vuln_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # Append the vulnerability to the list
            vulns.append(row)
        line_count += 1

# Open csv file of PR vulnerabilities
with open(input_pr_vuln_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # Append the vulnerability to the list
            vulns.append(row)
        line_count += 1

# Print out the total number of vulnerabilities (commit + PR)
# for which we calculated the time to release a fix
# and store the information into a csv file
logger.info(f"Total time intervals: {len(vulns)}")
with open(vulns_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Vuln ID', 'Package name', 'Clone dir',\
 'Commit hash', 'Release', 'Commit date', 'Release date', 'Time interval'])
    for i in range(0, len(vulns)):
        vulns_writer.writerow(vulns[i])

# -----------------------------------------------------------------------------------------
# Structure of packages CSV file: [Package name, Clone dir, Total vulns, Avg time interval]

# Open csv file of commit packages
with open(input_commit_packages_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # Append the package to the list, inserting 4 emmpty elements
            pkg_entry = [row[0], row[1], row[2], row[3], "", "", row[2], row[3]]
            packages.append(pkg_entry)
        line_count += 1

tot_packages = len(packages)
# Open csv file of PR packages
with open(input_pr_packages_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # If the package name is new, append it as new package,
            # otherwise modify the existing element calculating 
            # the total number of vulnerabilities and time interval average
            duplicated = False
            for j in range (0, tot_packages):
                if row[0] == packages[j][0]:
                    duplicated = True
                    # Insert PR vulnerabilities and avg time interval
                    packages[j][4] = row[2]
                    packages[j][5] = row[3]
                    # Calculate and insert total vulns and avg time interval
                    tot_vulns = int(packages[j][2]) + int(row[2])
                    tot_avg_time_interval = (int(packages[j][2]) * int(packages[j][3])) + (int(row[2]) * int(row[3]))
                    tot_avg_time_interval = int(tot_avg_time_interval / tot_vulns)
                    packages[j][6] = tot_vulns
                    packages[j][7] = tot_avg_time_interval
                    break
            if not duplicated:
                # Append the package to the list, inserting 4 emmpty elements
                pkg_entry = [row[0], row[1], "", "", row[2], row[3], row[2], row[3]]
                packages.append(pkg_entry)
                tot_packages += 1

        line_count += 1

# Print out the total number of packages (commit + PR)
# for which we calculated the time to release a fix
# and store the information into a csv file
logger.info(f"Total packages time intervals: {tot_packages}")
with open(packages_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
#    vulns_writer.writerow(['Package name', 'Clone dir', 'Commit vulns', 'Commit avg time interval',\
# 'PR vulns', 'PR avg time interval', 'Total vulns', 'Total avg time interval'])
    for i in range(0, tot_packages):
        vulns_writer.writerow(packages[i])