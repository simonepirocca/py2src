"""
This file correlates commit link of a vulnerability with the relative hash, package name and directory
"""
import sys
import os
import csv
import logging
import pytest
from pathlib import Path
import time

from ..src.vulns.vulns import Vuln
from ..src.utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/vulns.log")

# Set input and output files, inizialize variables
packages_input_file = "../output/vulns_output/packages_to_clone.csv"
commit_vulns_input_file = "../output/vulns_output/matching_vulns_unique_commit.csv"
pr_vulns_input_file = "../output/vulns_output/matching_vulns_unique_pr.csv"
commit_output_file = "../output/vulns_output/clone_dir_from_commit_hash.csv"
pr_output_file = "../output/vulns_output/clone_dir_from_pr_commit_hash.csv"

# Initialize variables
dirs = {}
commit_vulns = []
pr_vulns = []

# Open packages csv file
with open(packages_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            # For each package, get the name and clone URL, extracting the clone directory
            package_name = row[0]
            clone_url = row[1]
            package_dir = clone_url.split("/")[-1]
            package_dir = package_dir.replace(".git", "")

            # If the related directory has been cloned, 
            # append the package name and related directory in a dictionary
            if not os.path.isdir("../cloned_packages/" + package_dir):
                logger.info(f"Package '{package_name}' is not in directory {package_dir}'")
            else:
                dirs[package_name] = package_dir

        line_count += 1  

logger.info(f"Working on Commit vulns...")

# Open commit vulns csv file
with open(commit_vulns_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            # Get Vuln ID, severity, package name and commit URL of each vulnerability
            id = row[0]
            severity = row[1]
            name = row[4]
            commit_url = row[8]
            # Extract the hash out of the commit URL
            commit_hash = commit_url.split("/")[-1]
            hashtag_index = commit_hash.find("#")
            if hashtag_index != -1: commit_hash = commit_hash[:hashtag_index]
            question_index = commit_hash.find("?")
            if question_index != -1: commit_hash = commit_hash[:question_index]

            # If the vulnerability's package actually have some vulnerabilities 
            # with commit link associated, append it, its hash and the package directory
            if name in dirs and commit_hash != "":
                commit_vulns.append([id, severity, name, dirs[name], commit_hash])
            else: logger.info(f"{line_count}. Commit '{commit_hash}' is not related to package '{name}' or is empty")

        line_count += 1

logger.info(f"Working on PR vulns...")

# Open pr vulns csv file
with open(pr_vulns_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            # Get Vuln ID, severity, package name and PR URL of each vulnerability
            id = row[0]
            severity = row[1]
            name = row[4]
            pr_url = row[12]

            # If the PR link include the string "commit", it is already a commit link.
            # Otherwise, if it include the string "pull", try to get the related commit link crawling the page
            if "commit" in pr_url: commit_url = pr_url
            elif "pull" in pr_url: 
                pr_url = pr_url.replace("/files", "")
                time.sleep(3)
                commit_url = Vuln(pr_url).get_commit_link_from_pr_link()
            else: commit_url = ""

            if commit_url != "":
                if "https://" not in commit_url: commit_url = "https://github.com" + commit_url

                # Extract the hash out of the commit URL, if it is not empty
                commit_hash = commit_url.split("/")[-1]
                hashtag_index = commit_hash.find("#")
                if hashtag_index != -1: commit_hash = commit_hash[:hashtag_index]
                question_index = commit_hash.find("?")
                if question_index != -1: commit_hash = commit_hash[:question_index]

                # If the vulnerability's package actually have some vulnerabilities with commit link associated,
                # append it, its hash and commit url and the package directory
                if name in dirs and commit_hash != "":
                    pr_vulns.append([id, severity, name, dirs[name], commit_url, commit_hash])
                else: logger.info(f"{line_count}. Commit'{commit_hash}' is not related to package '{name}' or is empty")

            else: logger.info(f"{line_count}. Commit for PR Link '{pr_url}' of Vuln ID '{id}' didn't found")

        line_count += 1

# Print out the number of vulnerabilities
# and store the information into a csv file
logger.info(f"Commits: {len(commit_vulns)}, PR: {len(pr_vulns)}")

with open(commit_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Vuln ID', 'Severity','Package name', 'Clone dir', 'Commit hash'])
    for i in range(0, len(commit_vulns)):
        vulns_writer.writerow(commit_vulns[i])


with open(pr_output_file, mode='w') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    vulns_writer.writerow(['Vuln ID', 'Severity', 'Package name', 'Clone dir', 'Commit URL', 'Commit hash'])
    for i in range(0, len(pr_vulns)):
        vulns_writer.writerow(pr_vulns[i])