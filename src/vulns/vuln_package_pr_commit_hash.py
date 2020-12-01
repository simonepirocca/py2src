"""
This file correlate the PR url and relative commit link of a vulnerability with the relative package name and directory
"""
import sys
import os
import csv
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)

def test_find_package_from_vuln():
    dirs = {}
    commit_packages = []
    start = 41
    count = 20
    end = start + count

    with open('../../output/vulns_output/packages_with_vuln_pr.csv') as csv_file:
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
                else:
                    dirs[package_name] = clone_dir

            line_count += 1  

    with open('../../output/vulns_output/matching_vulns_unique_pr.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count >= start:

                id = row[0]
                name = row[4]
                pr_url = row[12]

                if "commit" in pr_url: commit_url = pr_url
                elif "pull" in pr_url: 
                    pr_url = pr_url.replace("/files", "")
                    commit_url = get_commit_from_pr(pr_url)
                    else: commit_url = ""

                #logging.info(f"PR url: {pr_url} --> Commit url: {commit_url}")

                if commit_url != "":
                    if "https://" not in commit_url: commit_url = "https://github.com" + commit_url
                    commit_hash = commit_url.split("/")[-1]
                    hashtag_index = commit_hash.find("#")
                    if hashtag_index != -1: commit_hash = commit_hash[:hashtag_index]
                    question_index = commit_hash.find("?")
                    if question_index != -1: commit_hash = commit_hash[:question_index]

                    if name in dirs and commit_hash != "":
                        commit_packages.append([id, name, dirs[name], commit_url, commit_hash])
                    else: logging.info(f"Commit'{commit_hash}' is not related to package '{name}' or is empty")

                else: logging.info(f"Commit for PR Link '{pr_url}' of Vuln ID '{id}' didn't found")

            line_count += 1
            if line_count >= end: break

    commits_found = len(commit_packages)
    commits_not_found = count - commits_found
    logging.info(f"Commits found: {commits_found},  Commit NOT found: {commits_not_found}")

    with open("../../output/vulns_output/clone_dir_from_pr_commit_hash.csv", mode='a') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        #vulns_writer.writerow(['Vuln ID', 'Package name', 'Clone dir', 'Commit url', 'Commit hash'])
        for i in range(0, len(commit_packages)):
            vulns_writer.writerow(commit_packages[i])


def get_commit_from_pr(url: str) -> str:
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(urlopen(req).read(), features="html.parser")
    except (ValueError, URLError, HTTPError, ConnectionResetError):
        return ""
    else:
        for div in soup.findAll("div"):
            # merged case
            div_text = div.getText()
            if "merged commit" in div_text:
                for link in div.findAll("a"):
                    try:
                        href_url = link["href"]
                    except KeyError:
                        # Link is not valid, go to the next line
                        continue
                    else:
                        if "/commit/" in href_url: return href_url

            # closed case
            elif "closed this" in div_text:
                for code in div.findAll("code"):
                    for link in code.findAll("a"):
                        try:
                            href_url = link["href"]
                        except KeyError:
                            # Link is not valid, go to the next line
                            continue
                        else:
                            if "/commit/" in href_url: return href_url

        # open case or not found
        return ""