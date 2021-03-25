import json
from urllib.request import Request, urlopen
from datetime import date
import pytest
from ..metrics.metrics import Metrics

class GetMetrics:
    def __init__(self, package_name: str, github_url:str):
        self._package_name = package_name
        self._github_url = github_url

    # Get the metrics and return the array
    def get_metrics(self):
        # Instanziate package
        github_url_parts = self._github_url.split("/")
        parts = len(github_url_parts)
        #github_token = "put_here_a_valid_github_token"
        pkg = Metrics(self._package_name, self._github_url)

        # Inizialize metrics
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

        # Get metrics using crawling functions
        open_issues = pkg.get_link_span_metric_from_github_repo("issues")
        closed_issues = pkg.get_closed_issues_from_github_repo()
        commits = pkg.get_commits_from_github_repo()
        releases = pkg.get_link_span_metric_from_github_repo("releases")
        if releases == "": releases = pkg.get_tags_from_github_repo()
        contributors = pkg.get_link_span_metric_from_github_repo("graphs/contributors")
        dependents_url = pkg.get_dependent_url_from_github_repo()
        dep_repos = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=REPOSITORY")
        dep_packages = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=PACKAGE")

        # Get 'stars' metrics and 'created_at' date using GItHub API
        github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
        api_req = Request(github_json_url)
        api_req.add_header('Authorization', 'token ' + github_token)
        try:
            github_json = json.loads(urlopen(api_req).read().decode())
            created_at = github_json["created_at"][:10]
            stargazers = github_json["stargazers_count"]
            if stargazers != "": stargazers = Metrics.convert_to_number(str(stargazers))
            #with open('../output/metrics_output/json/generic_data/' + package_name + '.json', 'w') as json_file:
            #    json.dump(github_json, json_file)
        except Exception:
            created_at = ""
            stargazers = ""

        # Get 'last_commit' metric using GItHub API
        commits_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "/commits"
        api_req = Request(commits_json_url)
        api_req.add_header('Authorization', 'token ' + github_token)
        try:
            commits_json = json.loads(urlopen(api_req).read().decode())
            last_commit = commits_json[0]["commit"]["author"]["date"][:10]
            #with open('../output/metrics_output/json/commits/' + package_name + '.json', 'w') as json_file:
            #    json.dump(commits_json, json_file)
        except Exception:
            last_commit = ""

        # Calculate total months and days from the creation date to now (needed for frequencies metrics)
        total_days = 0
        total_months = 0
        if created_at != "":
            today_date = date.today().strftime('%Y-%m-%d')
            total_months = (int(today_date[:4]) - int(created_at[:4])) * 12 + (int(today_date[5:7]) - int(created_at[5:7]))
            total_days = (int(today_date[:4]) - int(created_at[:4])) * 365 + (int(today_date[5:7]) - int(created_at[5:7])) * 30 + (int(today_date[8:]) - int(created_at[8:]))

        # Calculate 'commit_frequency' and 'release_frequency' metrics
        if total_months != 0 and commits != "":                
            commit_frequency = int(int(commits) / total_months)
        if total_days != 0 and releases != "":
            release_frequency = int(total_days / int(releases))

        # Calculate 'avg_close_issue_days' metric by inspecting most 100 recent closed issues
        i = 0
        api_closed_issues = 0
        sum_closed_days = 0
        issue_json_url = "https://api.github.com/search/issues?q=repo:" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "%20is:issue%20is:closed&per_page=100"
        api_req = Request(issue_json_url)
        api_req.add_header('Authorization', 'token ' + github_token)            
        # Get the json of closed issues using GitHub API
        try:
            issue_json = json.loads(urlopen(api_req).read().decode())
            #with open('../output/metrics_output/json/closed_issues/' + package_name + '.json', 'w') as json_file:
            #    json.dump(issue_json, json_file)
        except Exception:
            avg_close_issue_days = ""
        else:
            for i in range(len(issue_json["items"])):
                try:
                    # Get creation and close date for each issue
                    created_date = issue_json["items"][i]["created_at"][:10]
                    closed_date = issue_json["items"][i]["closed_at"][:10]
                except TypeError:
                    created_date = ""
                    closed_date = ""
                # Calculate for each issue the elapsed days
                if created_date != "" and closed_date != "":
                    close_days = (int(closed_date[:4]) - int(created_date[:4])) * 365 + (int(closed_date[5:7]) - int(created_date[5:7])) * 30 + (int(closed_date[8:]) - int(created_date[8:]))
                    sum_closed_days = sum_closed_days + close_days
                    api_closed_issues = api_closed_issues + 1
            # Compute the average
            if api_closed_issues > 0:
                avg_close_issue_days = int(sum_closed_days / api_closed_issues)
            else: api_closed_issues = ""

        metrics = [stargazers, last_commit, commit_frequency, release_frequency, open_issues, closed_issues, api_closed_issues, avg_close_issue_days, contributors, dep_repos, dep_packages]
        return metrics