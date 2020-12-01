"""
This file find the uncloned packages
"""
import sys
import os
import csv
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)


def test_find_uncloned_packages():
    input_file = "../../output/vulns_output/packages_with_vuln_pr.csv"
    output_file = "../../output/vulns_output/uncloned_pr_packages.csv"
    dirs = {}
    uncloned_packages = []

    with open(input_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                package_name = row[0]
                clone_url = row[1]
                clone_dir = clone_url.split("/")[-1]
                clone_dir = clone_dir.replace(".git", "")

                if not os.path.isdir("../../cloned_packages/" + clone_dir):
                    logging.info(f"Package '{package_name}' is not in directory {clone_dir}'")
                    uncloned_packages.append([package_name, clone_url, clone_dir])
            line_count += 1  

    
    with open(output_file, mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        vulns_writer.writerow(['Package name', 'Clone url', 'Clone dir'])
        for i in range(0, len(uncloned_packages)):
            vulns_writer.writerow(uncloned_packages[i])