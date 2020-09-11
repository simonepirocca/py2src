"""
This file get all the missing metrics for each repo
"""
import sys
import os
import csv
import json
from array import *
from datetime import date
from urllib.request import Request, urlopen
sys.path.append(os.path.abspath("../src/"))
from package import Package
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)

def test_fix_wrong_urls():

    start = 1
    count = 100
    end = start + count

    line_count = 0

    input_csv = "../metrics_output/wrong_urls.csv"
    output_csv = "../metrics_output/metrics_final_only_wrong_urls_fixed.csv"

    with open(output_csv, mode='w') as metrics_csv:
        packages_writer = csv.writer(metrics_csv, delimiter=';')
        packages_writer.writerow(['package_name', 'github_url', 'stars',\
 'last_commit', 'commit_freq', 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors',\
 'dep_repos', 'dep_pkgs'])

    with open(input_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if line_count >= start:
                package_name = row[0]
                github_url = row[1]

                if "#" in github_url: 
                    to_delete_index = github_url.index("#")
                    github_url = github_url[:to_delete_index]

                github_url_parts = github_url.split("/")
                parts = len(github_url_parts)
                github_token = "85ebe3db54f576a6c75c5431d8bd2caee157aeb9"
                pkg = Package(package_name)

                stargazers = ""
                last_commit = ""
                commit_frequency = ""
                release_frequency = ""
                open_issues = ""
                closed_issues = ""
                api_closed_issues = 0
                avg_close_issue_days = ""
                contributors = ""
                dep_repos = ""
                dep_packages = ""

                created_at = ""
                open_issues = pkg.get_link_span_metric_from_github_repo(github_url, "issues").strip()
                if open_issues != "": open_issues = convert_to_number(open_issues)
                issues_url = pkg.get_issues_url_from_github_repo(github_url).strip()
                closed_issues = pkg.get_closed_issues_from_github_repo(issues_url).strip()
                if closed_issues != "": closed_issues = convert_to_number(closed_issues)
                commits = pkg.get_commits_from_github_repo(github_url).strip()
                if commits != "": commits = convert_to_number(commits)
                releases = pkg.get_link_span_metric_from_github_repo(github_url, "releases").strip().replace(",", "")
                if releases == "": releases = pkg.get_tags_from_github_repo(github_url).strip()
                if releases != "": releases = convert_to_number(releases)
                contributors = pkg.get_link_span_metric_from_github_repo(github_url, "graphs/contributors").strip()
                if contributors != "": contributors = convert_to_number(contributors)
                dependents_url = pkg.get_dependent_url_from_github_repo(github_url).strip()
                dep_repos = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=REPOSITORY").strip()
                if dep_repos != "": dep_repos = convert_to_number(dep_repos)
                dep_packages = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=PACKAGE").strip()
                if dep_packages != "": dep_packages = convert_to_number(dep_packages)

                github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
                api_req = Request(github_json_url)
                api_req.add_header('Authorization', 'token ' + github_token)
                try:
                    github_json = json.loads(urlopen(api_req).read().decode())
                    created_at = github_json["created_at"][:10]
                    stargazers = github_json["stargazers_count"]
                    if stargazers != "": stargazers = convert_to_number(str(stargazers))

                    with open('../metrics_output/json/generic_data/' + package_name + '.json', 'w') as json_file:
                        json.dump(github_json, json_file)
                except Exception:
                    created_at = ""
                    stargazers = ""

                commits_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "/commits"
                api_req = Request(commits_json_url)
                api_req.add_header('Authorization', 'token ' + github_token)

                try:
                    commits_json = json.loads(urlopen(api_req).read().decode())
                    last_commit = commits_json[0]["commit"]["author"]["date"][:10]
                    with open('../metrics_output/json/commits/' + package_name + '.json', 'w') as json_file:
                        json.dump(commits_json, json_file)

                except Exception:
                    last_commit = ""

                total_days = 0
                total_months = 0
                if created_at != "":
                    today_date = date.today().strftime('%Y-%m-%d')
                    total_months = (int(today_date[:4]) - int(created_at[:4])) * 12 + (int(today_date[5:7]) - int(created_at[5:7]))
                    total_days = (int(today_date[:4]) - int(created_at[:4])) * 365 + (int(today_date[5:7]) - int(created_at[5:7])) * 30 + (int(today_date[8:]) - int(created_at[8:]))
                

                if total_months != 0 and commits != "":                
                    commit_frequency = int(int(commits) / total_months)

                if total_days != 0 and releases != "":
                    release_frequency = int(total_days / int(releases))

                i = 0
                api_closed_issues = 0
                sum_closed_days = 0

                issue_json_url = "https://api.github.com/search/issues?q=repo:" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "%20is:issue%20is:closed&per_page=100"
                api_req = Request(issue_json_url)
                api_req.add_header('Authorization', 'token ' + github_token)            

                try:
                    issue_json = json.loads(urlopen(api_req).read().decode())

                    with open('../metrics_output/json/closed_issues/' + package_name + '.json', 'w') as json_file:
                        json.dump(issue_json, json_file)

                except Exception:
                    avg_close_issue_days = ""
                else:
                    total_count = int(issue_json["total_count"])
                    for i in range(len(issue_json["items"])):
                        try:
                            created_date = issue_json["items"][i]["created_at"][:10]
                            closed_date = issue_json["items"][i]["closed_at"][:10]
                        except TypeError:
                            created_date = ""
                            closed_date = ""

                        if created_date != "" and closed_date != "":
                            close_days = (int(closed_date[:4]) - int(created_date[:4])) * 365 + (int(closed_date[5:7]) - int(created_date[5:7])) * 30 + (int(closed_date[8:]) - int(created_date[8:]))
                            sum_closed_days = sum_closed_days + close_days
                            api_closed_issues = api_closed_issues + 1

                    if api_closed_issues > 0:
                        avg_close_issue_days = int(sum_closed_days / api_closed_issues)
                    else: api_closed_issues = ""

                with open(output_csv, mode='a') as packages:
                    packages_writer = csv.writer(packages, delimiter=';')
                    packages_writer.writerow([package_name, github_url, stargazers,\
 last_commit, commit_frequency, release_frequency, open_issues, closed_issues, api_closed_issues, avg_close_issue_days,\
 contributors, dep_repos, dep_packages])

            line_count += 1
            if line_count >= end: break

def convert_to_number(n: str):
    n = n.replace("+", "").replace(",", "").replace("?", "")
    if "K" in n:
        if "." in n:
            dot_index = n.index(".")
            k_index = n.index("K")
            decimals = k_index - dot_index - 1
            if decimals == 1: return int(n.replace(".", "").replace("K", "")) * 100
            elif decimals == 2: return int(n.replace(".", "").replace("K", "")) * 10
        return int(n.replace("K", "")) * 1000
    if "k" in n:
        if "." in n:
            dot_index = n.index(".")
            k_index = n.index("k")
            decimals = k_index - dot_index - 1
            if decimals == 1: return int(n.replace(".", "").replace("k", "")) * 100
            elif decimals == 2: return int(n.replace(".", "").replace("k", "")) * 10
        return int(n.replace("k", "")) * 1000
    return int(n)