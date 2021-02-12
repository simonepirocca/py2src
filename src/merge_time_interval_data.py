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
    vulns_writer.writerow(['Vuln ID', 'Severity', 'Package name', 'Clone dir',\
 'Commit hash', 'Release', 'Release type', 'Commit date', 'Release date', 'Time interval'])
    for i in range(0, len(vulns)):
        vulns_writer.writerow(vulns[i])

# -----------------------------------------------------------------------------------------
# Structure of INPUT packages CSV file: [Package name, Clone dir, Tot vulns with commit, # Severity L, # Severity M,
#          # Severity H, Median severity, # Major v., # Minor v., # Patch v., Median release type, Avg time interval]


# Structure of OUTPUT packages CSV file: [Package name, Clone dir, Tot vulns, Commit vulns, PR vulns, Tot Severity L, Tot Severity M, Tot Severity H,
#           Median severity, Tot Major v., Tot Minor v., Tot Patch v., Median release type, Commit time interval, PR time interval, Avg time interval]

# Open csv file of commit packages
with open(input_commit_packages_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            # Append the package to the list, inserting 4 emmpty elements
            pkg_entry = [row[0], row[1], row[2], row[2], "", int(row[3]), int(row[4]), int(row[5]), row[6], int(row[7]), int(row[8]), int(row[9]), row[10], row[11], "", row[11]]
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
                    packages[j][14] = row[11]
                    # Calculate and insert total vulns and avg time interval
                    tot_vulns = int(packages[j][3]) + int(row[2])
                    tot_avg_time_interval = (int(packages[j][3]) * int(packages[j][13])) + (int(row[2]) * int(row[11]))
                    tot_avg_time_interval = int(tot_avg_time_interval / tot_vulns)
                    packages[j][2] = tot_vulns
                    packages[j][15] = tot_avg_time_interval
                    # Calculate and insert total severity and release type and related median
                    packages[j][5] += int(row[3])
                    packages[j][6] += int(row[4])
                    packages[j][7] += int(row[5])
                    if packages[j][5] >= packages[j][6] and packages[j][5] >= packages[j][7]: packages[j][8] = "L"
                    elif packages[j][6] >= packages[j][5] and packages[j][6] >= packages[j][7]: packages[j][8] = "M"
                    else: packages[j][8] = "H"
                    packages[j][9] += int(row[7])
                    packages[j][10] += int(row[8])
                    packages[j][11] += int(row[9])
                    if packages[j][9] >= packages[j][10] and packages[j][9] >= packages[j][11]: packages[j][12] = "major"
                    elif packages[j][10] >= packages[j][9] and packages[j][10] >= packages[j][11]: packages[j][12] = "minor"
                    else: packages[j][12] = "patch"
                    break
            if not duplicated:
                # Append the package to the list, inserting 4 emmpty elements
                pkg_entry = [row[0], row[1], row[2], "", row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], "", row[11], row[11]]
                packages.append(pkg_entry)
                tot_packages += 1

        line_count += 1

# Print out the total number of packages (commit + PR)
# for which we calculated the time to release a fix
# and store the information into a csv file
logger.info(f"Total packages time intervals: {tot_packages}")
with open(packages_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
#    vulns_writer.writerow([Package name, Clone dir, Tot vulns, Commit vulns, PR vulns, Tot Severity L, Tot Severity M, Tot Severity H,\
# Median Severity, Tot Major v., Tot Minor v., Tot Patch v., Median release type, Commit time interval, PR time interval, Avg time interval])
    for i in range(0, tot_packages):
        vulns_writer.writerow(packages[i])