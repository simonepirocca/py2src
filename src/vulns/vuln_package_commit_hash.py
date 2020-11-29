"""
This file correlate commit link of a vulnerability with the relative package name and directory
"""
import sys
import os
import csv
from urllib.request import Request, urlopen
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)


def test_find_package_from_vuln():
    dirs = {}
    commit_packages = []

    with open('../../output/vulns_output/packages_with_vuln_commit.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                package_name = row[0]
                clone_url = row[1]
                package_dir = clone_url.split("/")[-1]
                package_dir = package_dir.replace(".git", "")

                if not os.path.isdir("../../cloned_packages/" + package_dir):
                    logging.info(f"Package '{package_name}' is not in directory {package_dir}'")
                else:
                    dirs[package_name] = package_dir

            line_count += 1  

    with open('../../output/vulns_output/matching_vulns_unique_commit.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                id = row[0]
                name = row[4]
                commit_url = row[8]
                commit_hash = commit_url.split("/")[-1]
                hashtag_index = commit_hash.find("#")
                if hashtag_index != -1: commit_hash = commit_hash[:hashtag_index]

                if name in dirs and commit_hash != "":
                    commit_packages.append([id, name, dirs[name], commit_hash])
                else: logging.info(f"Commit'{commit_hash}' is not related to package '{name}' or is empty")

            line_count += 1

    logging.info(f"Commits: {len(commit_packages)}")
    logging.info(f"First commit: {commit_packages[0]}")

    with open("../../output/vulns_output/clone_dir_from_commit_hash.csv", mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        #vulns_writer.writerow(['Vuln ID', 'Package name', 'Clone dir', 'Commit hash'])
        for i in range(0, len(commit_packages)):
            vulns_writer.writerow(commit_packages[i])