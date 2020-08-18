"""
This file contains the description of the Metrics class, needed
to collect the metrics about a specific repositoriy
"""
import sys
import os
import json
#import logging
import csv
from urllib.request import Request, urlopen
from package import Package
from datetime import date
sys.path.append(os.path.abspath("../src/"))
#logging.basicConfig(filename="log.log", level=logging.INFO)

class Metrics:

    @staticmethod
    def get_repo_metrics(package_name: str, downloads: str):
        # Set Package object
        pkg = Package(package_name)

        # Variables declaration
        stargazers = ""
        last_commit = ""
        commit_frequency = 0
        release_frequency = 0
        open_issues = ""
        closed_issues = ""
        api_closed_issues = 0
        avg_close_issue_days = 0
        contributors = ""
        dep_repos = ""
        dep_packages = ""
        sourcerank = ""
        dep_packages_io = ""
        dep_repos_io = ""

        # Get the GitHub repo URL
        github_url = pkg.extract_github_url()
        if(github_url != ""):

            # Get GitHub metrics

            #watchers = pkg.get_link_metric_from_github_repo(github_url, "watchers").strip()
            #stargazers = pkg.get_link_metric_from_github_repo(github_url, "stargazers").strip()
            #forks = pkg.get_link_metric_from_github_repo(github_url, "members").strip()
            #updated_at = pkg.get_updated_at_from_github_repo(github_url).strip()[:10]
            created_at = ""
            open_issues = pkg.get_link_span_metric_from_github_repo(github_url, "issues").strip()
            issues_url = pkg.get_issues_url_from_github_repo(github_url).strip()
            closed_issues = pkg.get_closed_issues_from_github_repo(issues_url).strip()
            closed_issues = closed_issues.replace(",", "")
            commits = pkg.get_commits_from_github_repo(github_url).strip()
            commits = commits.replace(",", "")
            #last_commit = pkg.get_updated_at_from_github_repo(github_url).strip()[:10]
            releases = pkg.get_link_span_metric_from_github_repo(github_url, "releases").strip()
            contributors = pkg.get_link_span_metric_from_github_repo(github_url, "graphs/contributors").strip()
            dependents_url = pkg.get_dependent_url_from_github_repo(github_url).strip()
            dep_repos = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=REPOSITORY").strip()
            dep_packages = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=PACKAGE").strip()

            github_url_parts = github_url.split("/")
            parts = len(github_url_parts)

            github_token = "put_here_a_valid_github_token"

            github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
            api_req = Request(github_json_url)
            api_req.add_header('Authorization', 'token ' + github_token)
            github_json = json.loads(urlopen(api_req).read().decode())

            created_at = github_json["created_at"][:10]
            stargazers = github_json["stargazers_count"]
            issues_url = github_json["issues_url"]

            with open('../metrics_output/json/generic_data/' + package_name + '.json', 'w') as json_file:
                json.dump(github_json, json_file)

            commits_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "/commits"
            api_req = Request(commits_json_url)
            api_req.add_header('Authorization', 'token ' + github_token)
            commits_json = json.loads(urlopen(api_req).read().decode())
            last_commit = commits_json[0]["commit"]["author"]["date"][:10]

            with open('../metrics_output/json/commits/' + package_name + '.json', 'w') as json_file:
                json.dump(commits_json, json_file)

            total_months = 0
            if created_at != "" and commits != "":
                today_date = date.today().strftime('%Y-%m-%d')
                total_months = (int(today_date[:4]) - int(created_at[:4])) * 12 + (int(today_date[5:7]) - int(created_at[5:7]))
                commit_frequency = int(int(commits) / total_months)

            if created_at != "" and releases != "":
                release_frequency = round((int(releases) / total_months), 2)

            i = 0
            api_closed_issues = 0
            sum_closed_days = 0
            #api_closed_issues = 0
            #sum_closed_months = 0

            #while count < int(closed_issues):
            #while True:
            #    i = i + 1
            #    issue_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "/issues/" + str(i)
            #    api_req = Request(issue_json_url)
            #    api_req.add_header('Authorization', 'token ' + github_token)

             #   try:
             #       issue_json = json.loads(urlopen(api_req).read().decode())
             #   except Exception:
             #       break
             #   else:
             #       if issue_json["state"] == "closed":
             #           created_date = issue_json["created_at"][:10]
             #           closed_date = issue_json["closed_at"][:10]
             #           count = count + 1

             #           if created_date != "" and closed_date != "":
             #               close_months = (int(closed_date[:4]) - int(created_date[:4])) * 12 + (int(closed_date[5:7]) - int(created_date[5:7]))
             #               sum_closed_months = sum_closed_months + close_months
             #               api_closed_issues = api_closed_issues + 1


            issue_json_url = "https://api.github.com/search/issues?q=repo:" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "%20is:issue%20is:closed&per_page=" + closed_issues
            api_req = Request(issue_json_url)
            api_req.add_header('Authorization', 'token ' + github_token)            

            try:
                issue_json = json.loads(urlopen(api_req).read().decode())

                with open('../metrics_output/json/closed_issues/' + package_name + '.json', 'w') as json_file:
                    json.dump(issue_json, json_file)

            except Exception:
                avg_close_issue_days = 0
            else:
                total_count = int(issue_json["total_count"])
                for i in range(len(issue_json["items"])):
                    created_date = issue_json["items"][i]["created_at"][:10]
                    closed_date = issue_json["items"][i]["closed_at"][:10]

                    if created_date != "" and closed_date != "":
                        #close_months = (int(closed_date[:4]) - int(created_date[:4])) * 12 + (int(closed_date[5:7]) - int(created_date[5:7]))
                        close_days = (int(closed_date[:4]) - int(created_date[:4])) * 365 + (int(closed_date[5:7]) - int(created_date[5:7])) * 30 + (int(closed_date[8:]) - int(created_date[8:]))
                        sum_closed_days = sum_closed_days + close_days
                        api_closed_issues = api_closed_issues + 1

                if api_closed_issues > 0:
                    avg_close_issue_days = int(sum_closed_days / api_closed_issues)

        # Get the Libraries.io repo URL
        libraries_io_url = pkg.extract_libraries_io_url()
        if(libraries_io_url != ""):

            # Get Libraries.io metrics
            sourcerank = pkg.get_sourcerank_from_libraries_io(libraries_io_url).strip()
            dep_packages_io = pkg.get_dep_packages_from_libraries_io(libraries_io_url).strip()
            dep_repos_io = pkg.get_dep_repos_from_libraries_io(libraries_io_url).strip()

        with open('../metrics_output/metrics.csv', mode='a') as packages:
            packages_writer = csv.writer(packages, delimiter=';')
            packages_writer.writerow([package_name, downloads, github_url, stargazers,\
 last_commit, commit_frequency, release_frequency, open_issues, closed_issues, api_closed_issues, avg_close_issue_days,\
 contributors, dep_repos, dep_packages, libraries_io_url, sourcerank, dep_packages_io, dep_repos_io])
