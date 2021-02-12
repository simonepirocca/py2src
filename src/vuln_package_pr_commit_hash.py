"""
This file correlate the PR url and relative commit link of a vulnerability with the relative package name and directory
"""
import sys
import os
import csv
import logging
import pytest
from pathlib import Path

vulns_module_path = Path().resolve() / "vulns"
sys.path.append(str(vulns_module_path))
from vulns import Vuln

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/vulns.log")

# Set input and output files, inizialize variables
packages_input_file = "../output/vulns_output/packages_with_vuln_pr.csv"
vulns_input_file = "../output/vulns_output/matching_vulns_unique_pr.csv"
output_file = "../output/vulns_output/clone_dir_from_pr_commit_hash.csv"
dirs = {}
commit_packages = []
start = 1
count = 20 # It breaks if looking at more than 20 elements at time
end = start + count

# Open packages csv file
with open(packages_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:

            # For each package, get the name and clone URL, extracting the clone directory
            package_name = row[0]
            clone_url = row[1]
            clone_dir = clone_url.split("/")[-1]
            clone_dir = clone_dir.replace(".git", "")

            # If the related directory has been cloned, 
            # append the package name and related directory in a dictionary
            if not os.path.isdir("../cloned_packages/" + clone_dir):
                logger.info(f"Package '{package_name}' is not in directory {clone_dir}'")
            else:
                dirs[package_name] = clone_dir

        line_count += 1  

# Open vulns csv file
with open(vulns_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:

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
                    commit_packages.append([id, severity, name, dirs[name], commit_url, commit_hash])
                else: logger.info(f"Commit'{commit_hash}' is not related to package '{name}' or is empty")

            else: logger.info(f"Commit for PR Link '{pr_url}' of Vuln ID '{id}' didn't found")

        line_count += 1
        if line_count >= end: break

# Print out the number of commit links found and NOT found
commits_found = len(commit_packages)
commits_not_found = count - commits_found
logger.info(f"Commits for PR link found: {commits_found},  Commit for PR link NOT found: {commits_not_found}")

# Store the information into a csv file
with open(output_file, mode='a') as csv_file:
    vulns_writer = csv.writer(csv_file, delimiter=';')
    #vulns_writer.writerow(['Vuln ID', 'Severity', 'Package name', 'Clone dir', 'Commit URL', 'Commit hash'])
    for i in range(0, len(commit_packages)):
        vulns_writer.writerow(commit_packages[i])