import pytest
import csv
from ..src.vulns import Vuln

class GetVulns:
    def __init__(self, package_name: str):
        self._package_name = package_name

    # Get the vulnerabilities and return the array
    def get_vulns(self):
        #Inizialize variables
        crawled_vulns_file = "../inputs/crawled_vulns.csv"
        tmp_vulns_file = "../tmp/tmp_vulns.csv"
        crawled_vulns = []
        vulnerabilities = []
        tot_vulns = 0
        github_links = []

        # Open the stored URLs file
        with open(crawled_vulns_file) as urls_csv_file:
            urls_reader = csv.reader(urls_csv_file, delimiter=';')
            line_count = 0
            for row in urls_reader:
                if line_count > 0:
                    severity = row[0]
                    vuln_package_name = row[3]
                    commit_url = row[7]
                    pr_url = row[11]

                    if vuln_package_name == self._package_name:
                        tot_vulns += 1
                        if commit_url != "" and commit_url not in github_links:
                            # Extract the hash out of the commit URL
                            commit_hash = commit_url.split("/")[-1]
                            hashtag_index = commit_hash.find("#")
                            if hashtag_index != -1: commit_hash = commit_hash[:hashtag_index]
                            question_index = commit_hash.find("?")
                            if question_index != -1: commit_hash = commit_hash[:question_index]
                            # If the commit hash is valid insert it into the list of vulnerabilities
                            if commit_hash != "":
                                github_links.append(commit_url)
                                vulnerabilities.append([severity, commit_hash])
                        elif pr_url != "" and pr_url not in github_links:
                            # Extract the the commit URL
                            if "commit" in pr_url: commit_url = pr_url
                            elif "pull" in pr_url: 
                                pr_url = pr_url.replace("/files", "")
                                commit_url = Vuln(pr_url).get_commit_link_from_pr_link()
                            else: commit_url = ""
                            if commit_url != "":
                                # Extract the hash out of the commit URL
                                if "https://" not in commit_url: commit_url = "https://github.com" + commit_url
                                commit_hash = commit_url.split("/")[-1]
                                hashtag_index = commit_hash.find("#")
                                if hashtag_index != -1: commit_hash = commit_hash[:hashtag_index]
                                question_index = commit_hash.find("?")
                                if question_index != -1: commit_hash = commit_hash[:question_index]
                                # If the commit hash is valid insert it into the list of vulnerabilities
                                if commit_hash != "":
                                    github_links.append(commit_url)
                                    vulnerabilities.append([severity, commit_hash])
                line_count += 1

        # Print tmp file of vulnerabilities
        with open(tmp_vulns_file, mode='w') as vulns_csv_file:
            vulns_writer = csv.writer(vulns_csv_file, delimiter=';')
            vulns_writer.writerow(['Severity', 'Commit hash'])
            for vuln in vulnerabilities: vulns_writer.writerow(vuln)

        return [tot_vulns, len(vulnerabilities)]